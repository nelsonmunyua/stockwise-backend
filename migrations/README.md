# 📦 StockWise Backend

This is the **backend service** for **StockWise**, an inventory management system built with **FastAPI**. It provides RESTful APIs for managing users, categories, products, orders, and order items.

The backend is designed with **clean architecture**, **SQLAlchemy ORM**, and **Alembic migrations**, making it suitable for learning, extension, and production hardening.

---

## 🧰 Tech Stack

* **Framework:** FastAPI
* **Language:** Python 3.9+
* **Database:** SQLite (development)
* **ORM:** SQLAlchemy
* **Migrations:** Alembic
* **Auth:** Basic auth (JWT optional / planned)

---

## 🚀 Features (Backend)

### 👤 User Management

* User registration
* User login
* Role support (`admin`, `staff`)
* Active / inactive users

### 🗂 Category Management

* Create categories
* Fetch all categories
* Delete categories
* One-to-many relationship with products

### 📦 Product Management

* Create products
* Assign products to categories
* Update quantity and pricing
* Soft delete support (optional)

### 🧾 Orders

* Create orders per user
* Automatic total calculation
* Fetch user or all orders

### 📄 Order Items

* Add multiple products to an order
* Automatic subtotal calculation
* Prices fetched from the database

---

## 🏛 Database Models Overview

### Users

* `id` (PK)
* `username`
* `email`
* `hashed_password`
* `role`
* `is_active`
* `created_at`

### Category

* `id` (PK)
* `name`
* `description`

### Product

* `id` (PK)
* `name`
* `price`
* `quantity`
* `category_id` (FK)

### Orders

* `id` (PK)
* `created_at`
* `total_amount`
* `user_id` (FK)

### Order Items

* `id` (PK)
* `product_id` (FK)
* `order_id` (FK)
* `quantity`
* `subtotal`

---

## 📁 Backend Structure

```
backend/
│── alembic/
│── crud/
│   ├── user.py
│   ├── category.py
│   ├── product.py
│   ├── order.py
│   └── order_items.py
│── routes/
│   ├── users.py
│   ├── categories.py
│   ├── products.py
│   ├── orders.py
│   └── order_items.py
│── schemas/
│   ├── user.py
│   ├── category.py
│   ├── product.py
│   ├── order.py
│   └── order_items.py
│── database.py
│── models.py
│── main.py
└── requirements.txt
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/nelsonmunyua/stockwise.git
cd stockwise/backend
```

### 2️⃣ Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run Database Migrations

```bash
alembic upgrade head
```

### 5️⃣ Start Development Server

```bash
uvicorn main:app --reload
```

Backend will be available at:

```
http://127.0.0.1:8000
```

---

## 📚 API Documentation

FastAPI automatically generates API documentation:

* **Swagger UI:** `http://127.0.0.1:8000/docs`
* **ReDoc:** `http://127.0.0.1:8000/redoc`

---

## 🔌 API Endpoints (Summary)

### Users

* `POST /users/register`
* `POST /users/login`
* `GET /users/`

### Categories

* `GET /categories/`
* `POST /categories/`
* `DELETE /categories/{id}`

### Products

* `GET /products/`
* `POST /products/`
* `GET /products/{id}`
* `DELETE /products/{id}`

### Orders

* `GET /orders/`
* `POST /orders/`
* `GET /orders/{id}`
* `DELETE /orders/{id}`

### Order Items

* `POST /order-items/`
* `GET /order-items/{order_id}`

---

## 🧪 Development Notes

* SQLite is used for simplicity; swap with PostgreSQL/MySQL for production
* Passwords are stored as hashed values
* Business logic is separated into CRUD modules
* Schemas enforce request/response validation

---

## 📌 Planned Improvements

* JWT authentication
* Role-based permissions
* Pagination & filtering
* Low-stock alerts
* Reporting & analytics

---

## 📜 License

MIT License — free to use for learning and portfolio projects.
