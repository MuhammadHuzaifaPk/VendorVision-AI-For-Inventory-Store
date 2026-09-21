from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class InventoryItemBase(BaseModel):
    id: Optional[str] = "SKU-000"
    sku: str
    name: str
    supplier_name: str
    supplier_email: Optional[str] = "supplier@example.com"
    current_stock: int = Field(default=0, ge=0)
    target_stock_level: int = Field(default=10, gt=0)
    daily_sales_rate: float = Field(default=1.0, gt=0)
    unit_cost: float = Field(default=0.0, ge=0)


class InventoryAnalysisRequest(BaseModel):
    items: List[InventoryItemBase]


class InventoryAnalysisResponse(BaseModel):
    success: bool = True
    items: List[Dict[str, Any]]
    summary: Dict[str, Any]


class EmailDraftRequest(BaseModel):
    supplier_name: str
    item_name: str
    sku: Optional[str] = ""
    suggested_qty: Optional[int] = 0
    unit_cost: Optional[float] = 0.0
    prompt: Optional[str] = None
    force_fallback: Optional[bool] = False


class EmailDraftResponse(BaseModel):
    success: bool = True
    email_content: str
    subject: Optional[str] = "Reorder & Supply Negotiation Request"
    body: Optional[str] = ""
    supplier_name: str
    supplier_email: Optional[str] = "supplier@example.com"
    item_name: str
    estimated_savings_negotiated: Optional[float] = 0.0
    mode_used: Optional[str] = "OpenAI GPT"


class SettingsUpdateRequest(BaseModel):
    ai_api_key: Optional[str] = None
    ai_model_name: Optional[str] = "gpt-4o-mini"
    enable_mock_fallback: Optional[bool] = True


class SettingsResponse(BaseModel):
    success: bool = True
    ai_configured: bool
    ai_model_name: str
    enable_mock_fallback: bool
    status_message: str


class UploadResponse(BaseModel):
    status: str
    message: str
    uploaded_items_count: int
    summary: Dict[str, Any]
    items: List[Dict[str, Any]]


class HealthCheckResponse(BaseModel):
    status: str
    project: str
    version: str
    ai_engine_active: bool