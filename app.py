import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models import get_db, User, Category, Product, Order, OrderItems
from sqlalchemy.orm import Session
from sqlalchemy import func

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "https://stockwise-frontend-weld.vercel.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ USER SCHEMAS & ENDPOINTS ============
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "staff"
    is_active: bool = True

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


@app.get("/users")
def get_users(session: Session = Depends(get_db)):
    users = session.query(User).all()
    return users

@app.get("/users/{user_id}")
def get_user(user_id: int, session: Session = Depends(get_db)):
    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users")
def create_user(user: UserCreate, session: Session = Depends(get_db)):
    existing = session.query(User).filter(User.username == user.username).first()
    if existing is None:
        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=user.password,
            role=user.role,
            is_active=True
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return {"message": "User created successfully"}
    else:
        return {"message": "User already exists"}

@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserCreate, session: Session = Depends(get_db)):
    existing_user = session.query(User).filter(User.id == user_id).first()
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing_user.username = user.username
    existing_user.email = user.email
    existing_user.hashed_password = user.password
    existing_user.role = user.role
    existing_user.is_active = user.is_active
    
    session.commit()
    session.refresh(existing_user)
    return {"message": "User updated successfully", "user": existing_user}

@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_db)):
    existing_user = session.query(User).filter(User.id == user_id).first()
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    session.delete(existing_user)
    session.commit()
    return {"message": "User deleted successfully"}

# ============ CATEGORY SCHEMAS & ENDPOINTS ============
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    products_count: Optional[int] = 0

@app.get("/categories")
def get_categories(session: Session = Depends(get_db)):
    categories = session.query(Category).all()
    return categories

@app.get("/categories/{category_id}")
def get_category(category_id: int, session: Session = Depends(get_db)):
    category = session.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Get products count
    products_count = session.query(func.count(Product.id)).filter(
        Product.category_id == category_id
    ).scalar()
    
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "products_count": products_count
    }

@app.post("/categories")
def create_category(category: CategoryCreate, session: Session = Depends(get_db)):
    new_category = Category(
        name=category.name,
        description=category.description
    )
    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    return {"message": "Category created successfully", "category": new_category}

@app.put("/categories/{category_id}")
def update_category(category_id: int, category: CategoryCreate, session: Session = Depends(get_db)):
    existing_category = session.query(Category).filter(Category.id == category_id).first()
    if existing_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    existing_category.name = category.name
    existing_category.description = category.description
    
    session.commit()
    session.refresh(existing_category)
    return {"message": "Category updated successfully", "category": existing_category}

@app.delete("/categories/{category_id}")
def delete_category(category_id: int, session: Session = Depends(get_db)):
    existing_category = session.query(Category).filter(Category.id == category_id).first()
    if existing_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if category has products
    products_count = session.query(func.count(Product.id)).filter(
        Product.category_id == category_id
    ).scalar()
    
    if products_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete category with existing products")
    
    session.delete(existing_category)
    session.commit()
    return {"message": "Category deleted successfully"}

# ============ PRODUCT SCHEMAS & ENDPOINTS ============
class ProductCreate(BaseModel):
    name: str
    price: int
    quantity: int
    category_id: int

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    quantity: Optional[int] = None
    category_id: Optional[int] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    quantity: int
    category_id: int
    category_name: Optional[str] = None

@app.get("/products")
def get_products(session: Session = Depends(get_db)):
    products = session.query(
        Product.id,
        Product.name,
        Product.price,
        Product.quantity,
        Product.category_id,
        Category.name.label("category_name")
    ).join(Category, Product.category_id == Category.id).all()
    
    return [{
        "id": p.id,
        "name": p.name,
        "price": p.price,
        "quantity": p.quantity,
        "category_id": p.category_id,
        "category_name": p.category_name
    } for p in products]

@app.get("/products/{product_id}")
def get_product(product_id: int, session: Session = Depends(get_db)):
    product = session.query(
        Product.id,
        Product.name,
        Product.price,
        Product.quantity,
        Product.category_id,
        Category.name.label("category_name")
    ).join(Category, Product.category_id == Category.id).filter(
        Product.id == product_id
    ).first()
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity,
        "category_id": product.category_id,
        "category_name": product.category_name
    }

@app.post("/products")
def create_product(product: ProductCreate, session: Session = Depends(get_db)):
    # Check if category exists
    category = session.query(Category).filter(Category.id == product.category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    new_product = Product(
        name=product.name,
        price=product.price,
        quantity=product.quantity,
        category_id=product.category_id
    )
    
    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    return {"message": "Product created successfully", "product": new_product}

@app.put("/products/{product_id}")
def update_product(product_id: int, product_update: ProductUpdate, session: Session = Depends(get_db)):
    product = session.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update fields if provided
    if product_update.name is not None:
        product.name = product_update.name
    if product_update.price is not None:
        product.price = product_update.price
    if product_update.quantity is not None:
        product.quantity = product_update.quantity
    if product_update.category_id is not None:
        # Verify new category exists
        category = session.query(Category).filter(Category.id == product_update.category_id).first()
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        product.category_id = product_update.category_id
    
    session.commit()
    session.refresh(product)
    return {"message": "Product updated successfully", "product": product}

@app.delete("/products/{product_id}")
def delete_product(product_id: int, session: Session = Depends(get_db)):
    product = session.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    session.delete(product)
    session.commit()
    return {"message": "Product deleted successfully"}

# ============ ORDER SCHEMAS & ENDPOINTS ============
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    price: int
    subtotal: int

class OrderResponse(BaseModel):
    id: int
    created_at: datetime
    total_amount: int
    user_id: int
    username: str
    items: List[OrderItemResponse]

@app.get("/orders")
def get_orders(session: Session = Depends(get_db)):
    orders = session.query(
        Order.id,
        Order.created_at,
        Order.total_amount,
        Order.user_id,
        User.username
    ).join(User, Order.user_id == User.id).all()
    
    return [{
        "id": o.id,
        "created_at": o.created_at,
        "total_amount": o.total_amount,
        "user_id": o.user_id,
        "username": o.username
    } for o in orders]

@app.get("/orders/{order_id}")
def get_order(order_id: int, session: Session = Depends(get_db)):
    order = session.query(
        Order.id,
        Order.created_at,
        Order.total_amount,
        Order.user_id,
        User.username
    ).join(User, Order.user_id == User.id).filter(
        Order.id == order_id
    ).first()
    
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get order items
    order_items = session.query(
        OrderItems.id,
        OrderItems.product_id,
        OrderItems.quantity,
        OrderItems.subtotal,
        Product.name.label("product_name"),
        Product.price
    ).join(Product, OrderItems.product_id == Product.id).filter(
        OrderItems.order_id == order_id
    ).all()
    
    return {
        "id": order.id,
        "created_at": order.created_at,
        "total_amount": order.total_amount,
        "user_id": order.user_id,
        "username": order.username,
        "items": [{
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product_name,
            "quantity": item.quantity,
            "price": item.price,
            "subtotal": item.subtotal
        } for item in order_items]
    }

@app.post("/orders")
def create_order(order_data: OrderCreate, session: Session = Depends(get_db)):
    # Verify user exists
    user = session.query(User).filter(User.id == order_data.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate total amount and validate stock
    total_amount = 0
    order_items_data = []
    
    for item in order_data.items:
        # Get product and check stock
        product = session.query(Product).filter(Product.id == item.product_id).first()
        if product is None:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        if product.quantity < item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient stock for product {product.name}. Available: {product.quantity}"
            )
        
        # Calculate subtotal
        subtotal = product.price * item.quantity
        total_amount += subtotal
        
        # Reduce product quantity
        product.quantity -= item.quantity
        
        # Prepare order item data
        order_items_data.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "subtotal": subtotal,
            "product": product
        })
    
    # Create order
    new_order = Order(
        user_id=order_data.user_id,
        total_amount=total_amount
    )
    session.add(new_order)
    session.flush()  # Get the order ID without committing
    
    # Create order items
    for item_data in order_items_data:
        order_item = OrderItems(
            order_id=new_order.id,
            product_id=item_data["product_id"],
            quantity=item_data["quantity"],
            subtotal=item_data["subtotal"]
        )
        session.add(order_item)
    
    session.commit()
    session.refresh(new_order)
    
    return {
        "message": "Order created successfully",
        "order_id": new_order.id,
        "total_amount": total_amount
    }

@app.get("/")
def index():
    return {"name": "StockWise API", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)