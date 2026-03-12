from fastapi import FastAPI, Query, Path, Body
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()

# --- DAY 1 DATA (Needed for Day 2) ---
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False}, # Note: Out of stock
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

orders = [] # For the Bonus task
   


# --- DAY 2 MODELS (Q3 & Q5) ---
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1)

feedback_db = []

# --- DAY 2 ENDPOINTS ---

# Q1: Filter with min_price
@app.get("/products/filter")
def filter_products(category: str = None, max_price: int = None, min_price: int = None):
    result = products
    if category:
        result = [p for p in result if p['category'].lower() == category.lower()]
    if max_price:
        result = [p for p in result if p['price'] <= max_price]
    if min_price:
        result = [p for p in result if p['price'] >= min_price]
    return result

# Q2: Get Price Only
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    p = next((x for x in products if x["id"] == product_id), None)
    return {"name": p["name"], "price": p["price"]} if p else {"error": "Product not found"}

# Q3: POST Feedback
@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback_db.append(data.dict())
    return {"message": "Feedback submitted successfully", "total_feedback": len(feedback_db)}

# Q4: Product Summary
@app.get("/products/summary")
def get_summary():
    return {
        "total_products": len(products),
        "in_stock_count": len([p for p in products if p["in_stock"]]),
        "out_of_stock_count": len([p for p in products if not p["in_stock"]]),
        "most_expensive": max(products, key=lambda x: x['price']),
        "cheapest": min(products, key=lambda x: x['price']),
        "categories": list(set(p['category'] for p in products))
    }

# Q5: Bulk Orders (Validation Logic)
@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed, failed, total = [], [], 0
    for item in order.items:
        p = next((x for x in products if x["id"] == item.product_id), None)
        if not p or not p["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": "Not found or Out of Stock"})
        else:
            subtotal = p["price"] * item.quantity
            total += subtotal
            confirmed.append({"product": p["name"], "qty": item.quantity, "subtotal": subtotal})
    return {"company": order.company_name, "confirmed": confirmed, "failed": failed, "grand_total": total}

# BONUS: Order Tracking
@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    return {"order_id": order_id, "status": "confirmed"}
