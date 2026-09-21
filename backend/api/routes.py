import io
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from urllib.parse import quote
import pandas as pd

from services.ai_engine import AIEngineService
from core.config import settings

router = APIRouter()

# In-memory application state
COMMUNICATIONS_DB = []
INVENTORY_DB = []

REQUIRED_EXCEL_COLUMNS = [
    "sku", "name", "current_stock", 
    "target_stock_level", "daily_sales_rate", 
    "unit_cost", "supplier_name"
]

class InventoryItem(BaseModel):
    sku: str
    name: str
    current_stock: int
    target_stock_level: int
    daily_sales_rate: float
    unit_cost: float
    supplier_name: str

class InventoryAnalysisRequest(BaseModel):
    items: List[InventoryItem]

class DraftEmailRequest(BaseModel):
    supplier_name: str
    item_name: str
    unit_cost: float
    suggested_qty: int

class SettingsUpdateRequest(BaseModel):
    ai_api_key: Optional[str] = None
    ai_model_name: Optional[str] = "gemini-3.5-flash"
    enable_mock_fallback: Optional[bool] = False

# --- Inventory & Dashboard Endpoints ---

@router.post("/inventory/analyze")
async def analyze_inventory(data: InventoryAnalysisRequest):
    global INVENTORY_DB
    engine = AIEngineService()
    INVENTORY_DB = [item.model_dump() for item in data.items]
    return engine.analyze_inventory(INVENTORY_DB)

@router.get("/inventory")
@router.get("/dashboard/data")
async def get_dashboard_data():
    """
    Returns store inventory content and real-time analytics for the dashboard UI.
    """
    engine = AIEngineService()
    analysis = engine.analyze_inventory(INVENTORY_DB)
    return {
        "status": "success",
        "total_items": len(INVENTORY_DB),
        "summary": analysis.get("summary", {}),
        "items": analysis.get("items", [])
    }

@router.delete("/inventory/clear")
async def clear_inventory():
    """Wipes out current store inventory from dashboard."""
    global INVENTORY_DB
    INVENTORY_DB.clear()
    return {"status": "success", "message": "Inventory wiped out successfully."}

# --- Settings & Custom Excel Upload Endpoints ---

@router.post("/settings/upload-excel")
async def upload_custom_excel(file: UploadFile = File(...)):
    """
    Uploads custom store Excel file, validates schema, updates dashboard state,
    and returns calculated inventory analytics.
    """
    global INVENTORY_DB
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file format. Upload an Excel (.xlsx or .xls) file.")

    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Normalize column headers
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

        # Validate required columns
        missing_cols = [col for col in REQUIRED_EXCEL_COLUMNS if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=422, 
                detail=f"Missing required columns: {', '.join(missing_cols)}. Download sample PDF for structure."
            )

        # Parse and sanitize data rows
        parsed_items = []
        for _, row in df.iterrows():
            parsed_items.append({
                "sku": str(row["sku"]),
                "name": str(row["name"]),
                "current_stock": int(row["current_stock"]),
                "target_stock_level": int(row["target_stock_level"]),
                "daily_sales_rate": float(row["daily_sales_rate"]),
                "unit_cost": float(row["unit_cost"]),
                "supplier_name": str(row["supplier_name"])
            })

        INVENTORY_DB = parsed_items
        engine = AIEngineService()
        analysis = engine.analyze_inventory(INVENTORY_DB)

        return {
            "status": "success",
            "message": f"Successfully loaded {len(INVENTORY_DB)} items from {file.filename}",
            "uploaded_items_count": len(INVENTORY_DB),
            "summary": analysis.get("summary", {}),
            "items": analysis.get("items", [])
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process Excel file: {str(e)}")

@router.get("/settings/sample-template-pdf")
async def download_sample_pdf_guide():
    """
    Generates and downloads a Sample Structure Guide PDF showing required Excel formatting.
    """
    pdf_content = (
        "%PDF-1.4\n"
        "1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
        "2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
        "3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources <</Font <</F1 5 0 R>>>>>> endobj\n"
        "4 0 obj <</Length 280>> stream\n"
        "BT /F1 16 Tf 50 720 Td (VendorVision AI - Excel Import Guide) Tj ET\n"
        "BT /F1 12 Tf 50 680 Td (Ensure your Excel file contains the following exact column headers:) Tj ET\n"
        "BT /F1 10 Tf 50 640 Td (1. sku | 2. name | 3. current_stock | 4. target_stock_level) Tj ET\n"
        "BT /F1 10 Tf 50 620 Td (5. daily_sales_rate | 6. unit_cost | 7. supplier_name) Tj ET\n"
        "endstream endobj\n"
        "5 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica>> endobj\n"
        "xref\n0 6\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000242 00000 n\n0000000574 00000 n\n"
        "trailer <</Size 6 /Root 1 0 R>>\nstartxref\n645\n%%EOF"
    )
    return StreamingResponse(
        io.BytesIO(pdf_content.encode('latin-1')),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Excel_Format_Structure_Guide.pdf"}
    )

# --- Supplier & Email Endpoints ---

@router.get("/supplier/communications")
async def get_supplier_communications():
    return {"status": "success", "communications": COMMUNICATIONS_DB}

@router.post("/supplier/communications")
@router.post("/supplier/draft-email")
async def draft_and_log_email(data: DraftEmailRequest):
    engine = AIEngineService()
    try:
        result = engine.generate_supplier_email(
            supplier_name=data.supplier_name,
            item_name=data.item_name,
            unit_cost=data.unit_cost,
            suggested_qty=data.suggested_qty
        )
        
        email_body = result.get("email_content") or result.get("body") or ""
        result["body"] = email_body
        result["email_content"] = email_body

        recipient = result.get("supplier_email", "")
        subject = result.get("subject", "")
        
        result["mailto_link"] = f"mailto:{recipient}?subject={quote(subject)}&body={quote(email_body)}"
        COMMUNICATIONS_DB.append(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/supplier/communications/clear")
async def clear_communications():
    global COMMUNICATIONS_DB
    COMMUNICATIONS_DB.clear()
    return {"status": "success", "message": "Communications log cleared."}

# --- Settings Config Endpoints ---

@router.get("/settings")
async def get_settings():
    masked_key = ""
    if settings.GEMINI_API_KEY:
        masked_key = settings.GEMINI_API_KEY[:6] + "..." + settings.GEMINI_API_KEY[-4:]

    return {
        "ai_model_name": settings.DEFAULT_GEMINI_MODEL,
        "enable_mock_fallback": settings.ENABLE_MOCK_FALLBACK,
        "is_configured": settings.is_ai_configured(),
        "masked_api_key": masked_key
    }

@router.post("/settings")
async def update_settings(data: SettingsUpdateRequest):
    if data.ai_api_key and data.ai_api_key.strip():
        settings.GEMINI_API_KEY = data.ai_api_key.strip()
    if data.ai_model_name:
        settings.DEFAULT_GEMINI_MODEL = data.ai_model_name
    if data.enable_mock_fallback is not None:
        settings.ENABLE_MOCK_FALLBACK = data.enable_mock_fallback

    return {
        "status_message": "Gemini API key and settings updated successfully!",
        "is_configured": settings.is_ai_configured()
    }