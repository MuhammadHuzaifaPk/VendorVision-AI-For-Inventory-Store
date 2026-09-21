from typing import List
from models.schemas import InventoryItemBase, InventoryItem

def analyze_inventory(items: List[InventoryItemBase]) -> List[InventoryItem]:
    """
    Core algorithm to process inventory items, calculate forecasting metrics,
    and prioritize reorders based on stock status.
    """
    analyzed_items = []
    
    for item in items:
        # Calculate days until stockout based on current inventory and daily sales velocity
        if item.daily_sales_rate > 0:
            days_until_stockout = round(item.current_stock / item.daily_sales_rate, 2)
        else:
            days_until_stockout = 999.0  # Safe fallback for non-moving items

        # Determine stock status severity
        if item.current_stock <= item.reorder_point:
            if days_until_stockout <= 3:
                status = "CRITICAL"
            else:
                status = "LOW"
        else:
            status = "OK"

        # Calculate optimal reorder quantity to reach target stock
        suggested_qty = max(0, item.target_stock_level - item.current_stock)
        estimated_cost = round(suggested_qty * item.unit_cost, 2)

        # Generate a unique ID simulating a database primary key
        item_id = f"prod_{hash(item.sku) % 1000000:06x}"

        analyzed_items.append(
            InventoryItem(
                **item.model_dump(),
                id=item_id,
                stock_status=status,
                days_until_stockout=days_until_stockout,
                suggested_reorder_qty=suggested_qty,
                estimated_reorder_cost=estimated_cost
            )
        )
        
    return analyzed_items