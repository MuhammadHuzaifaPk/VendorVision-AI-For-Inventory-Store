import json
import os
from google import genai
from google.genai import types
from core.config import settings

class AIEngineService:
    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name or settings.DEFAULT_GEMINI_MODEL or "gemini-3.6-flash"

        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def generate_supplier_email(self, supplier_name: str, item_name: str, unit_cost: float, suggested_qty: int) -> dict:
        if not self.client:
            if settings.ENABLE_MOCK_FALLBACK:
                return self._get_mock_email(supplier_name, item_name, unit_cost, suggested_qty)
            raise ValueError("GEMINI_API_KEY is not configured. Add your free Gemini API Key in .env or Settings.")

        total_order_val = unit_cost * suggested_qty

        prompt = f"""
        You are an expert AI procurement manager at VendorVision AI.
        Draft an urgent, highly professional restock and pricing negotiation email to a supplier.

        Context:
        - Supplier: {supplier_name}
        - Product Item: {item_name}
        - Current Unit Cost: ${unit_cost:.2f}
        - Quantity to Order: {suggested_qty} units
        - Total Estimated PO Value: ${total_order_val:.2f}

        Instructions:
        1. Write a unique, context-aware business email asking for an immediate restock order.
        2. Politely negotiate a volume discount (between 5% to 10%) based on order size.
        3. Do NOT use generic placeholders or brackets like [Your Name]—sign off cleanly as "VendorVision AI Procurement Team".
        4. Return output strictly in valid JSON format with keys:
           - "supplier_email": string
           - "subject": string
           - "email_content": string
           - "estimated_savings_negotiated": float (calculate exact negotiated savings in USD)
        """

        try:
            # Recommended approach: Initialize a chat session and use send_message
            chat = self.client.chats.create(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3,
                )
            )

            response = chat.send_message(prompt)
            data = json.loads(response.text)

            return {
                "supplier_email": data.get("supplier_email", f"orders@{supplier_name.lower().replace(' ', '')}.com"),
                "subject": data.get("subject", f"Urgent Purchase Order Request - {item_name}"),
                "email_content": data.get("email_content", response.text),
                "estimated_savings_negotiated": float(data.get("estimated_savings_negotiated", total_order_val * 0.07)),
                "mode_used": f"Gemini Live ({self.model_name})"
            }
        except Exception as e:
            if settings.ENABLE_MOCK_FALLBACK:
                mock = self._get_mock_email(supplier_name, item_name, unit_cost, suggested_qty)
                mock["mode_used"] = f"Fallback (Gemini Error: {str(e)})"
                return mock
            raise RuntimeError(f"Gemini Generation Failed: {str(e)}")

    def analyze_inventory(self, inventory_items: list) -> dict:
        processed_items = []
        total_reorder_val = 0.0
        critical_count = 0
        warning_count = 0

        for item in inventory_items:
            daily_rate = item.get("daily_sales_rate", 1.0) or 1.0
            curr_stock = item.get("current_stock", 0)
            target_stock = item.get("target_stock_level", 50)
            unit_cost = item.get("unit_cost", 10.0)

            days_left = int(curr_stock / daily_rate) if daily_rate > 0 else 999
            suggested_qty = max(0, target_stock - curr_stock)

            if days_left <= 3:
                status = "CRITICAL"
                critical_count += 1
            elif days_left <= 10:
                status = "WARNING"
                warning_count += 1
            else:
                status = "HEALTHY"

            est_cost = suggested_qty * unit_cost
            total_reorder_val += est_cost

            processed_items.append({
                **item,
                "stock_status": status,
                "days_until_stockout": days_left,
                "suggested_reorder_qty": suggested_qty,
                "estimated_reorder_cost": est_cost
            })

        return {
            "summary": {
                "total_items_analyzed": len(inventory_items),
                "critical_stockouts": critical_count,
                "low_stock_warnings": warning_count,
                "total_estimated_reorder_value": total_reorder_val
            },
            "items": processed_items
        }

    def _get_mock_email(self, supplier_name, item_name, unit_cost, suggested_qty):
        total = unit_cost * suggested_qty
        savings = total * 0.075
        return {
            "supplier_email": f"orders@{supplier_name.lower().replace(' ', '')}.com",
            "subject": f"Urgent Restock Request - {item_name}",
            "email_content": f"Dear {supplier_name} Account Team,\n\nWe identified stock depletion for {item_name}.\n\nWe request {suggested_qty} units with a target 7.5% volume discount.\n\nBest regards,\nProcurement Team",
            "estimated_savings_negotiated": savings,
            "mode_used": "Mock Fallback"
        }

ai_engine = AIEngineService()