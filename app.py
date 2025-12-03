import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from models import get_db, User, Category, Product, Order, OrderItems


app = FastAPI()

# allow network requests from all servers
# app.add_middleware(CORSMiddleware, allow_origins= ["*"], allow_methods=["*"])
origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )
# create routes to access resources

@app.get("/")
def index():
    return {"name": "First Data"}

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "staff"
    is_active: bool = True


# class UserResponse(BaseModel):
#     id: int
#     username: str
#     email: str
#     role: str
#     is_active: str
#     created_at: str

# http://localhost/8000 -> GET -> retrieve all users
@app.get("/users")
def get_users(session = Depends(get_db)):
    #use sql alchemy to retrieve all users
    users = session.query(User).all()
    return users



# http://localhost:8000/users -> POST -> create a single user
@app.post("/users")
def create_user(user: UserCreate, session = Depends(get_db)):
    # check if the user exists
    existing = session.query(User).filter(User.username == user.username).first()

    if existing is None:
        # persist to db
        # 1. create an instance of the user class(model) with the details

        # hashed the password
        
        new_user = User(username = user.username, email = user.email, hashed_password = user.password, role = user.role, is_active = True)
        # 2. add the instance to the transaction
        session.add(new_user)
        # 3. commit the transaction
        session.commit()
        # 4. refresh the connection
        session.refresh(new_user)
        # return a message that the user has been created
        return {"message": "User created successfully"}    
    else:
        return {"message": "user already exists"}
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
