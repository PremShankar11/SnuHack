from fastapi import APIRouter, UploadFile, File, HTTPException
import json
from services.ingestion_pipeline import parse_receipt_image, reconcile_receipt

router = APIRouter()

@router.post("/api/ingest/receipt")
async def ingest_receipt(file: UploadFile = File(...)):
    """
    Triggers the OCR pipeline:
    1. Parses the image using Gemini 1.5 Pro.
    2. Runs N-Way Reconciliation on the extracted data.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
        
    try:
        contents = await file.read()
        
        # 1. Vision OCR
        parsed_data = parse_receipt_image(contents, mime_type=file.content_type)
        
        # 2. N-Way Reconciliation
        reconciliation_result = reconcile_receipt(parsed_data)
        
        return {
            "message": "Receipt processed successfully",
            "parsed_receipt": parsed_data,
            "reconciliation": reconciliation_result
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
