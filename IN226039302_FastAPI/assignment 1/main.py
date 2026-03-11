from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

app = FastAPI()

# --- Mock Data from Day 1 ---
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

feedback_store = []
orders_store = {}  # For Bonus: Store orders by ID


# --- 1. Easy: Query Parameters (Filtered Products) ---
@app.get("/products/filter")
def filter_products(
        min_price: int = Query(0, ge=0),
        max_price: Optional[int] = None,
        category: Optional[str] = None
):
    results = products
    if min_price:
        results = [p for p in results if p["price"] >= min_price]
    if max_price:
        results = [p for p in results if p["price"] <= max_price]
    if category:
        results = [p for p in results if p["category"].lower() == category.lower()]
    return results


# --- 2. Easy: Path Parameter (Specific Fields) ---
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return {"error": "Product not found"}
    return {"name": product["name"], "price": product["price"]}


# --- 3. Medium: Pydantic + POST (Feedback) ---
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback_item = data.model_dump()
    feedback_store.append(feedback_item)
    return {
        "message": "Feedback submitted successfully",
        "feedback": feedback_item,
        "total_feedback": len(feedback_store)
    }


# --- 4. Medium: Business Logic (Summary Dashboard) ---
@app.get("/products/summary")
def get_inventory_summary():
    in_stock = [p for p in products if p["in_stock"]]
    out_of_stock = [p for p in products if not p["in_stock"]]

    # Sorting to find most/least expensive
    sorted_products = sorted(products, key=lambda x: x["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_of_stock),
        "most_expensive": {"name": sorted_products[-1]["name"], "price": sorted_products[-1]["price"]},
        "cheapest": {"name": sorted_products[0]["name"], "price": sorted_products[0]["price"]},
        "categories": list(set(p["category"] for p in products))
    }


# --- 5. Hard: Bulk Order Logic ---
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)


class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str  # Use EmailStr if pydantic[email] is installed
    items: List[OrderItem] = Field(..., min_items=1)


@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
        elif not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
        else:
            subtotal = product["price"] * item.quantity
            confirmed.append({
                "product": product["name"],
                "qty": item.quantity,
                "subtotal": subtotal
            })
            grand_total += subtotal

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }


# --- ⭐ Bonus: Order Tracking & PATCH ---
@app.post("/orders")
def create_order(item: OrderItem):
    # Simplified for the bonus tracker
    order_id = len(orders_store) + 1
    orders_store[order_id] = {"item": item, "status": "pending"}
    return {"order_id": order_id, "status": "pending"}


@app.get("/orders/{order_id}")
def get_order_status(order_id: int):
    if order_id not in orders_store:
        return {"error": "Order not found"}
    return orders_store[order_id]


@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    if order_id not in orders_store:
        return {"error": "Order not found"}
    orders_store[order_id]["status"] = "confirmed"
    return {"message": f"Order {order_id} confirmed", "status": "confirmed"}
