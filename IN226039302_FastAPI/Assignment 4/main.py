from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

# ==================================================
# FASTAPI APP
# ==================================================

app = FastAPI()

# ==================================================
# DAY 1 ASSIGNMENT STARTS HERE
# ==================================================

# -------------------------
# PRODUCTS DATABASE
# -------------------------

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 599, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "USB Cable", "price": 199, "category": "Electronics", "in_stock": False},
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False}
]

# -------------------------
# ROOT ENDPOINT
# -------------------------

@app.get("/")
def home():
    return {"message": "FastAPI Store API Running"}

# -------------------------
# DAY1 Q1 — GET ALL PRODUCTS
# -------------------------

@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }

# -------------------------
# DAY1 Q2 — CATEGORY FILTER
# -------------------------

@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):

    result = [
        p for p in products
        if p["category"].lower() == category_name.lower()
    ]

    if not result:
        return {"error": "No products found in this category"}

    return {
        "category": category_name,
        "products": result,
        "total": len(result)
    }

# -------------------------
# DAY1 Q3 — IN STOCK PRODUCTS
# -------------------------

@app.get("/products/instock")
def get_instock():

    available = [
        p for p in products
        if p["in_stock"] == True
    ]

    return {
        "in_stock_products": available,
        "count": len(available)
    }

# -------------------------
# DAY1 Q4 — STORE SUMMARY
# -------------------------

@app.get("/store/summary")
def store_summary():

    in_stock_count = len([p for p in products if p["in_stock"]])
    out_stock_count = len(products) - in_stock_count
    categories = list(set([p["category"] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock_count,
        "out_of_stock": out_stock_count,
        "categories": categories
    }

# -------------------------
# DAY1 Q5 — SEARCH PRODUCTS
# -------------------------

@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    results = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]

    if not results:
        return {"message": "No products matched your search"}

    return {
        "keyword": keyword,
        "results": results,
        "total_matches": len(results)
    }

# -------------------------
# DAY1 BONUS — BEST DEAL
# -------------------------

@app.get("/products/deals")
def get_deals():

    cheapest = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }



# ==================================================
# DAY 2 ASSIGNMENT STARTS HERE
# ==================================================

# -------------------------
# DAY2 Q1 — FILTER PRODUCTS
# -------------------------

@app.get("/products/filter")
def filter_products(
    category: str = Query(None),
    min_price: int = Query(None),
    max_price: int = Query(None)
):

    result = products

    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]

    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    return {"filtered_products": result}


# -------------------------
# DAY2 Q2 — PRODUCT PRICE
# -------------------------

@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }

    return {"error": "Product not found"}


# -------------------------
# DAY2 Q3 — CUSTOMER FEEDBACK
# -------------------------

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


feedback = []


@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    feedback.append(data.dict())

    return {
        "message": "Feedback submitted successfully",
        "feedback": data.dict(),
        "total_feedback": len(feedback)
    }


# -------------------------
# DAY2 Q4 — PRODUCT SUMMARY
# -------------------------

@app.get("/products/summary")
def product_summary():

    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]

    expensive = max(products, key=lambda p: p["price"])
    cheapest = min(products, key=lambda p: p["price"])

    categories = list(set(p["category"] for p in products))

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive": expensive,
        "cheapest": cheapest,
        "categories": categories
    }


# -------------------------
# DAY2 Q5 — BULK ORDER
# -------------------------

class OrderItem(BaseModel):
    product_id: int
    quantity: int


class BulkOrder(BaseModel):
    company_name: str
    contact_email: str
    items: List[OrderItem]


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
            failed.append({"product_id": item.product_id, "reason": "Out of stock"})

        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal

            confirmed.append({
                "product": product["name"],
                "quantity": item.quantity,
                "subtotal": subtotal
            })

    return {
        "company": order.company_name,
        "confirmed_orders": confirmed,
        "failed_orders": failed,
        "grand_total": grand_total
    }


# -------------------------
# DAY2 BONUS — ORDER STATUS TRACKER
# -------------------------

orders = []

# POST /orders  (create order with pending status)

class OrderRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


@app.post("/orders")
def place_order(order: OrderRequest):

    product = next((p for p in products if p["id"] == order.product_id), None)

    if not product:
        return {"error": "Product not found"}

    if not product["in_stock"]:
        return {"error": "Product out of stock"}

    order_data = {
        "order_id": len(orders) + 1,
        "product": product["name"],
        "quantity": order.quantity,
        "status": "pending"
    }

    orders.append(order_data)

    return {
        "message": "Order placed successfully",
        "order": order_data
    }


# GET /orders/{order_id}

@app.get("/orders/{order_id}")
def get_order(order_id: int):

    for order in orders:
        if order["order_id"] == order_id:
            return {"order": order}

    return {"error": "Order not found"}


# PATCH /orders/{order_id}/confirm

@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"

            return {
                "message": "Order confirmed",
                "order": order
            }



# ==================================================
# DAY 3 ASSIGNMENT STARTS HERE
# ==================================================

# -------------------------
# DAY3 Q1 — ADD PRODUCT
# -------------------------

class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True

@app.post("/products/add")
def add_product(product: NewProduct):

    new_id = max(p["id"] for p in products) + 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    return {
        "message": "Product added successfully",
        "product": new_product
    }

# -------------------------
# DAY3 Q2 — UPDATE PRODUCT
# -------------------------

@app.put("/products/update/{product_id}")
def update_product(product_id: int, price: Optional[int] = None, in_stock: Optional[bool] = None):

    for product in products:

        if product["id"] == product_id:

            if price is not None:
                product["price"] = price

            if in_stock is not None:
                product["in_stock"] = in_stock

            return {
                "message": "Product updated successfully",
                "updated_product": product
            }

    return {"error": "Product not found"}

# -------------------------
# DAY3 Q3 — DELETE PRODUCT
# -------------------------

@app.delete("/products/delete/{product_id}")
def delete_product(product_id: int):

    for product in products:

        if product["id"] == product_id:

            products.remove(product)

            return {
                "message": "Product deleted successfully",
                "deleted_product": product
            }

    return {"error": "Product not found"}

# -------------------------
# DAY3 Q4 — PRODUCT AUDIT
# -------------------------

@app.get("/products/audit")
def product_audit():

    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]

    total_value = sum(p["price"] for p in in_stock)

    most_expensive = max(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_products": [p["name"] for p in out_stock],
        "total_stock_value": total_value,
        "most_expensive_product": most_expensive
    }

# -------------------------
# DAY3 Q5 — ORDER SUMMARY
# -------------------------

@app.get("/orders/summary")
def order_summary():

    total_feedback = len(feedback)

    avg_rating = 0

    if total_feedback > 0:
        avg_rating = sum(f["rating"] for f in feedback) / total_feedback

    return {
        "total_feedback_received": total_feedback,
        "average_rating": round(avg_rating, 2)
    }

# -------------------------
# DAY3 BONUS — DISCOUNT
# -------------------------

@app.put("/products/discount")
def apply_discount(category: str = Query(...), discount_percent: int = Query(..., ge=1, le=90)):

    updated_products = []

    for product in products:

        if product["category"].lower() == category.lower():

            discount_amount = product["price"] * discount_percent / 100
            product["price"] = int(product["price"] - discount_amount)

            updated_products.append(product)

    if not updated_products:
        return {"message": "No products found in this category"}

    return {
        "category": category,
        "discount_percent": discount_percent,
        "updated_products": updated_products
    }


# ==================================================
# DAY 4 ASSIGNMENT STARTS HERE
# ==================================================

# -------------------------
# CART DATABASE
# -------------------------

cart = []

# -------------------------
# DAY4 Q1 — ADD ITEMS TO CART
# -------------------------

@app.post("/cart/add")
def add_to_cart(product_id: int = Query(...), quantity: int = Query(1)):

    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    for item in cart:
        if item["product_id"] == product_id:

            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * product["price"]

            return {
                "message": "Cart updated",
                "cart_item": item
            }

    subtotal = product["price"] * quantity

    cart_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": subtotal
    }

    cart.append(cart_item)

    return {
        "message": "Added to cart",
        "cart_item": cart_item
    }

# -------------------------
# DAY4 Q2 — VIEW CART
# -------------------------

@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }

# -------------------------
# DAY4 Q3 — ERROR HANDLING
# -------------------------
# handled automatically in add_to_cart()

# -------------------------
# DAY4 Q4 — UPDATE CART ITEM
# -------------------------
# handled automatically in add_to_cart()

# -------------------------
# DAY4 Q5 — REMOVE ITEM
# -------------------------

@app.delete("/cart/{product_id}")
def remove_item(product_id: int):

    for item in cart:

        if item["product_id"] == product_id:

            cart.remove(item)

            return {"message": f"Product {product_id} removed from cart"}

    raise HTTPException(status_code=404, detail="Product not in cart")

# -------------------------
# CHECKOUT MODEL
# -------------------------

class CheckoutRequest(BaseModel):

    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)

# -------------------------
# DAY4 Q5 — CHECKOUT
# -------------------------

@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):

    if not cart:

        raise HTTPException(
            status_code=400,
            detail="Cart is empty — add items first"
        )

    created_orders = []
    grand_total = 0

    for item in cart:

        order = {
            "order_id": len(orders) + 1,
            "customer_name": data.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"],
            "delivery_address": data.delivery_address
        }

        orders.append(order)

        created_orders.append(order)

        grand_total += item["subtotal"]

    cart.clear()

    return {
        "message": "Checkout successful",
        "orders_placed": created_orders,
        "grand_total": grand_total
    }

# -------------------------
# DAY4 Q5 — VIEW ORDERS
# -------------------------

@app.get("/orders")
def get_orders():

    return {
        "orders": orders,
        "total_orders": len(orders)
    }

# -------------------------
# DAY4 Q6 — MULTI CUSTOMER FLOW
# -------------------------
# works automatically

# -------------------------
# DAY4 BONUS — EMPTY CART CHECK
# -------------------------
# handled inside checkout()
