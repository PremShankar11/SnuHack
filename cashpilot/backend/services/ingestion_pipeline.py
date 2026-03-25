import os
import json
import google.generativeai as genai
from rapidfuzz import fuzz

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db import get_db_connection

# Ensure API key is configured
api_key = os.environ.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

def parse_receipt_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    """
    Uses Gemini 1.5 Pro to parse receipt image into strict JSON.
    Expected schema matches ingestion_event from shared_contracts.json.
    """
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY is not set in the environment.")
        
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = '''
    Analyze this receipt image and extract the data into a strict JSON payload.
    Do not include markdown blocks, only raw JSON.
    The JSON structure MUST exactly match this format:
    {
        "ingestion_event": {
            "source": "GEMINI_VISION_OCR",
            "raw_text_reference": "Extracted text snippet...",
            "parsed_data": {
                "entity_name": "Name of the Vendor",
                "entity_type": "VENDOR",
                "amount": -123.45,
                "due_date": "YYYY-MM-DD"
            },
            "reconciliation_confidence": 0.95
        }
    }
    '''
    image_parts = [
        {
            "mime_type": mime_type,
            "data": image_bytes
        }
    ]
    
    response = model.generate_content([prompt, image_parts[0]])
    try:
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:-3]
        elif text.startswith('```'):
            text = text[3:-3]
        return json.loads(text.strip())
    except Exception as e:
        print("Failed to parse Gemini output:", response.text)
        raise e

def reconcile_receipt(parsed_data: dict) -> dict:
    """
    N-Way Reconciliation: Uses rapidfuzz to check scanned receipts against the obligations table.
    Matches if Amount matches AND Name similarity > 80%.
    If matched -> Merge records.
    If no match -> Create new pending obligation.
    """
    event = parsed_data.get('ingestion_event', parsed_data)
    pd = event.get('parsed_data', {})
    
    amount = pd.get('amount')
    entity_name = pd.get('entity_name')
    due_date = pd.get('due_date')
    
    if not amount or not entity_name or not due_date:
        raise ValueError("Missing required fields in parsed receipt data.")
        
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT id, name FROM entities WHERE entity_type = 'VENDOR';")
        entities = cur.fetchall()
        
        matched_entity_id = None
        for entity in entities:
            # Name similarity > 80%
            if fuzz.ratio(entity['name'].lower(), entity_name.lower()) > 80:
                matched_entity_id = entity['id']
                break
                
        if not matched_entity_id:
            cur.execute("SELECT id FROM companies LIMIT 1;")
            company = cur.fetchone()
            if company:
                cur.execute(
                    "INSERT INTO entities (company_id, name, entity_type, ontology_tier) "
                    "VALUES (%s, %s, %s, %s) RETURNING id;",
                    (company['id'], entity_name, 'VENDOR', 3) # default tier = 3
                )
                matched_entity_id = cur.fetchone()['id']
            else:
                raise Exception("No company found to associate new entity with.")

        cur.execute("SELECT id, amount FROM obligations WHERE status = 'PENDING' AND entity_id = %s;", (matched_entity_id,))
        pending_obs = cur.fetchall()
        
        matched_ob_id = None
        for ob in pending_obs:
            # Exact match on amount
            if abs(float(ob['amount']) - float(amount)) < 0.01:
                matched_ob_id = ob['id']
                break
                
        if matched_ob_id:
            # Merge records: Mark obligation as PAID, log a transaction
            cur.execute("UPDATE obligations SET status = 'PAID' WHERE id = %s;", (matched_ob_id,))
            cur.execute(
                "INSERT INTO transactions (entity_id, amount, cleared_date, source) "
                "VALUES (%s, %s, CURRENT_DATE, %s);",
                (matched_entity_id, amount, 'RECEIPT_OCR')
            )
            result_action = f"Merged with existing obligation {matched_ob_id}"
        else:
            # No match: Create new pending obligation
            cur.execute(
                "INSERT INTO obligations (entity_id, amount, due_date, status) "
                "VALUES (%s, %s, %s, %s) RETURNING id;",
                (matched_entity_id, amount, due_date, 'PENDING')
            )
            new_id = cur.fetchone()['id']
            result_action = f"Created new pending obligation {new_id}"

        conn.commit()
        
        return {
            "status": "success",
            "action": result_action,
            "entity": entity_name,
            "amount": amount
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
