# import the necessary packages
from datetime import datetime
from sqlalchemy import Column, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import create_engine

# create an engine which essentially is responsible for converting sql to python and vicevercer
engine = create_engine("sqlite:///stockwise.db", echo=True)

# create session which allows us to interface with the db

Session = sessionmaker(bind=engine)

# for fastapi we need to craete a method that return the session

def get_db():
    session = Session()
    try:
        # returns the session we can use to interact with the db via fastapi methods
        yield session
    finally:
        # this closes the connection to the db
        session.close()

# set a base class from which all our models will inherit from

Base = declarative_base()

# -----------------------
#     USERS MODEL
# -----------------------

class User(Base):
    # initialize the table name via the attribute __tablename__

    __tablename__ = "users"

    id = Column(Integer(), primary_key=True)
    username = Column(Text(), unique=True, nullable=False, index=True)
    email = Column(Text(), nullable=False, unique=True, index=True)
    hashed_password = Column(Text(), nullable=False)
    role = Column(Text(), nullable=False, default="staff")
    is_active = Column(Boolean(), default=True)
    created_at = Column(DateTime, default= datetime.now())

    # relationship -> user has many orders
    orders = relationship("Orders", back_populates="user")

    #  --------------------
    #    CATEGORY MODEL
    # ---------------------

class Category(Base):
    __tablename__ = "category"

    id = Column(Integer(), primary_key=True)
    name = Column(Text(), nullable=False)
    description = Column(Text())

        # relationship category has many products
    products = relationship("Products", back_populates="category")

        # ------------------
        #   PRODUCT MODEL
        # ------------------

class Product(Base):
    __tablename__ = "product"

    id = Column(Integer(), primary_key=True)
    name = Column(Text(), nullable=False)
    price = Column(Integer(), nullable=False)
    quantity = Column(Integer(), nullable=False)
    category_id = Column(Integer(), ForeignKey("category_id"), nullable=False)

            # relationship

    category = relationship("Category", back_populates = "products")
    orders_items = relationship("OrderItems", back_populates="product")

            # ------------------
            #   ORDERS MODEL
            # ------------------

class Orders(Base):
    __tablename__ = "orders"

    id = Column(Integer(), primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    total_amount = Column(Integer())
    user_id = Column(Integer(), ForeignKey("users.id"), nullable=False)

                # relationship
    user = relationship("Users", back_populates="order")
    items = relationship("OrderItems", back_populates="order")


                # -------------------
                #    ORDER ITEMS MODEL
                # -------------------
                
class OrderItems(Base):
    __tablename__ = "order_items"

    id = Column(Integer(), primary_key=True)
    product_id = Column(Integer(), ForeignKey("product.id"), nullable=False)
    order_id = Column(Integer(), ForeignKey("orders.id"), nullable=False)
    quantity = Column(Integer(), nullable=False)
    subtotal = Column(Integer(), nullable=False)

    # relationship
    product = relationship("Product", back_populates="order_items")
    order = relationship("Orders", back_populates="items")

                
    



