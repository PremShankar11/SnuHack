import os
import json
import tempfile
import pymupdf4llm
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

def process_pdf_to_contract(file_bytes: bytes) -> dict:
    """
    Process PDF invoice/bill and extract structured data.
    
    Args:
        file_bytes: PDF file content as bytes
        
    Returns:
        dict: Structured JSON matching ingestion_event schema
    """
    print(f"📄 Extracting layout-aware Markdown from PDF...")
    
    # Create a temporary file to store the PDF bytes
    temp_pdf = None
    try:
        # 1. Write bytes to a temporary file (pymupdf4llm needs a file path)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            temp_pdf.write(file_bytes)
            temp_pdf_path = temp_pdf.name
        
        # 2. Convert PDF to Markdown (Preserves tables and structure)
        md_text = pymupdf4llm.to_markdown(temp_pdf_path)
        
        # 3. Feed Markdown to Gemini for Structural Parsing
        prompt = f"""You are a financial data extractor. Below is a Markdown representation of a PDF invoice/bill.

Extract the details into this exact JSON structure:

{{
  "ingestion_event": {{
    "source": "PDF_OCR",
    "raw_text_reference": "Brief excerpt from the document",
    "parsed_data": {{
      "entity_name": "Name of the vendor or sender",
      "entity_type": "VENDOR",
      "amount": -100.00,
      "due_date": "YYYY-MM-DD",
      "is_receivable": false
    }},
    "reconciliation_confidence": 0.95
  }}
}}

CRITICAL RULES:
- Return ONLY valid JSON, no markdown code blocks.
- For INVOICES/BILLS you need to PAY: amount MUST be NEGATIVE (e.g., -1500.00)
- For RECEIPTS showing you already PAID: amount MUST be NEGATIVE (e.g., -1500.00)
- For INCOME/RECEIVABLES (money coming to you): amount should be positive
- If no due_date is found, use the invoice date or document date
- entity_type should be "VENDOR" for bills/invoices, "CUSTOMER" for receivables
- is_receivable should be false for money going OUT, true for money coming IN
- Set reconciliation_confidence between 0.0 and 1.0 based on data clarity
- Extract the EXACT vendor/entity name as it appears in the document

DATA:
{md_text}
"""
        
        print("🤖 Sending Markdown to Gemini for JSON structuring...")
        response = model.generate_content(prompt)
        
        try:
            # Clean response text in case Gemini adds markdown code blocks
            json_str = response.text.replace('```json', '').replace('```', '').strip()
            parsed_json = json.loads(json_str)
            
            print("✅ Successfully parsed PDF to structured data")
            return parsed_json
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse Gemini response as JSON: {e}")
            print(f"Raw response: {response.text}")
            raise ValueError(f"Invalid JSON response from Gemini: {str(e)}")
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error processing PDF: {error_msg}")
        
        # Check if it's a quota error
        if "429" in error_msg or "quota" in error_msg.lower():
            raise Exception(f"Gemini API quota exceeded. Please wait a few minutes or upgrade your API plan. Error: {error_msg}")
        else:
            raise Exception(f"PDF processing failed: {error_msg}")
    finally:
        # Clean up temporary file
        if temp_pdf and os.path.exists(temp_pdf_path):
            try:
                os.unlink(temp_pdf_path)
            except:
                pass
