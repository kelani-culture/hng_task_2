from typing import Annotated, List

from auth import JwtGenerator, login_required
from db import SessionLocal, engine
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from models import Base, Organization, User
from schemas import (
    UserData,
    UserLoginSchema,
    UserPostSchema,
    UserResponseSchema,
    UserDataSchema,
    UserDetailSchema
)
from sqlalchemy.orm import Session
from utils import (
    hash_password,
    post_login_response,
    post_response,
    verify_password,
)

Base.metadata.create_all(bind=engine)


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post(
    "/auth/register",
    status_code=201,
    response_model=UserResponseSchema,
    responses=post_response,
)
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
    exist_user = db.query(User).filter(User.email == user.email).first()
    if exist_user:
        content = {
            "status": "Bad Request",
            "message": "User already exist",
            "status_code": 400,
        }
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content=content
        )
    db.add(user)
    db.commit()
    db.refresh(user)
    user_dict = user.to_dict()
    dct, _ = get_user_and_access_token(user_dict, "Registration successful")
    response = JSONResponse(status_code=201, content=dct)
    return response


@app.post(
    "/auth/login",
    response_model=UserResponseSchema,
    responses=post_login_response,
)
def login_user(user: UserLoginSchema, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.email == user.email).first()
    password = (
        verify_password(user.password, user_db.password) if user_db else None
    )
    if not user_db or not password:
        detail = {
            "status": "Bad request",
            "message": "Authentication failed",
            "statusCode": 401,
        }
        return HTTPException(status_code=401, detail=detail)
    user_dict = user_db.to_dict()
    message = "Login successful"
    dct, access_token = get_user_and_access_token(user_dict, message)
    response = JSONResponse(status_code=201, content=dct)
    response.set_cookie(key="token", value=access_token, httponly=True)
    return response


def get_user_and_access_token(user_dict: dict, message: str):
    """
    get user from the database and add access token to their response
    """
    user_id = {"userId": user_dict["userId"]}
    access_token = JwtGenerator.create_access_token(user_id)
    user_info = UserData(**{"access_token": access_token, "user": user_dict})
    resp = UserResponseSchema(
        status="success", message=message, data=user_info
    )
    return resp.model_dump(), access_token


@app.get("/api/users/{id}", response_model=UserDetailSchema)
@login_required
def get_user(request: Request, id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.userId == id).first()
    if user:
        user_dict = user.to_dict()
        user_info = UserDataSchema(**user_dict)
        response = UserDetailSchema(
            status="success", message="User found", data=user_info
        ).model_dump()
        return response

    return JSONResponse(status_code=404, content={"message": "User not found"})


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
