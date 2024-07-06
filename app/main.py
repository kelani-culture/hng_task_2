from typing import Annotated, List

from db import SessionLocal, engine
from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from models import Base, Organization, User
from pydantic import ValidationError
from schemas import UserPostSchema, UserResponseSchema, UserData, UserLoginSchema
from sqlalchemy.orm import Session
from utils import hash_password, post_response
from validators import JwtGenerator

Base.metadata.create_all(bind=engine)


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/auth/register", status_code=201, response_model=UserResponseSchema, responses=post_response)
def create_user(user: UserPostSchema, db: Session = Depends(get_db)):
    """
    Handle user creation account
    """
    password = hash_password(password=user.password)
    user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=password,
        phone=user.phone,
    )
    exist_user = db.query(User).filter(User.email==user.email).first()
    if exist_user:
        content = {"status": "Bad Request", "message": "User already exist", "status_code": 400}
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=content)
    db.add(user)
    db.commit()
    db.refresh(user)
    user_dict = user.to_dict()
    user_id = {'userId': user_dict['userId']}
    print(user_dict)
    access_token = JwtGenerator.create_access_token(user_id)
    user_info = UserData(**{'access_token': access_token, 'user': user_dict})
    response = UserResponseSchema(status="success", message="Registration successful", data=user_info)
    return response


@app.exception_handler(RequestValidationError)
def custom_request_validation_error(
    request: Request, exc: RequestValidationError
):
    """
    handles the user validation error response
    """
    error = [
        {"fields": err["loc"][1], "message": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"errors": error},
    )



@app.get('/auth/login')
def login_user(user: UserLoginSchema, db: Session = Depends(get_db)):
    ...