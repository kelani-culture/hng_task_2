from typing import Annotated, List

from app.auth import JwtGenerator, login_required
from app.db import SessionLocal, engine
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.middleware import CustomAuthenticationMiddleWare
from app.models import Base, Organization, User
from app.schemas import (
    OrgBaseSchema,
    OrgResponseSchema,
    OrgSchema,
    UserData,
    UserDataSchema,
    UserDetailSchema,
    UserLoginSchema,
    UserOrganizationSchema,
    UserOrganizationSchemaResponse,
    UserOrgResponseSchema,
    UserOrgSchema,
    UserPostSchema,
    UserResponseSchema,
)
from sqlalchemy.orm import Session
from starlette.middleware.authentication import AuthenticationMiddleware


from app.utils import hash_password, post_login_response, post_response, verify_password
Base.metadata.create_all(bind=engine)


app = FastAPI()


# custom middle ware added
app.add_middleware(
    AuthenticationMiddleware, backend=CustomAuthenticationMiddleWare()
)


# get database session
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
            "message": "Registration unsuccessful",
            "statusCode": 400,
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
    db.close()
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
        return JSONResponse(status_code=401, content=detail)
    user_dict = user_db.to_dict()
    message = "Login successful"
    dct, access_token = get_user_and_access_token(user_dict, message)
    response = JSONResponse(status_code=200, content=dct)
    response.set_cookie(key="token", value=access_token, httponly=True)
    db.close()
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
    db.close()
    return JSONResponse(status_code=404, content={"message": "User not found"})


@app.get("/api/organisations", response_model=UserOrgResponseSchema)
@login_required
def get_all_user_organisaton(request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.userId == request.user.username).first()
    if not user:
        return JSONResponse(
            status_code=404, content={"message": "user not found"}
        )

    user_org = UserOrgSchema(
        organisations=[
            OrgSchema(
                orgId=str(org.orgId),
                name=org.name,
                description=org.description,
            )
            for org in user.organizations
        ]
    )
    response = UserOrgResponseSchema(
        status="success", message="organization fetched", data=user_org
    )
    db.close()
    return response


@app.get("/api/organisations/{orgId}", response_model=OrgResponseSchema)
@login_required
def get_single_organisation(
    request: Request, orgId: str, db: Session = Depends(get_db)
):
    """
    get a single organization user is associated with
    """
    user_org = (
        db.query(Organization).filter(Organization.orgId == orgId).first()
    )
    if not user_org:
        content = {
            "status": "Bad request",
            "message": "Organisation Not Found",
            "statusCode": 401,
        }
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content=content
        )
    user_dict = user_org.to_dict()
    user_org = OrgSchema(**user_dict)
    response = OrgResponseSchema(
        status="success", message="Organization found", data=user_dict
    )
    db.close()
    return response


@app.post(
    "/api/organisations", status_code=201, response_model=OrgResponseSchema
)
@login_required
def create_organization(
    request: Request, org: OrgBaseSchema, db: Session = Depends(get_db)
):
    """
    create user organization
    """
    existing_org = (
        db.query(Organization).filter(Organization.name == org.name).first()
    )
    if existing_org:
        detail = {
            "status": "Unsuccessful request",
            "message": "Client error",
            "statusCode": 400,
        }
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content=detail
        )
    user = db.query(User).filter(User.userId == request.user.username).first()
    add_org = Organization(name=org.name, description=org.description)
    add_org.users.append(user)
    db.add(add_org)
    db.commit()
    db.refresh(add_org)

    org_dict = add_org.to_dict()
    added_org = OrgSchema(**org_dict)
    response = OrgResponseSchema(
        status="Success",
        message="Organisation created successfully",
        data=added_org,
    )
    db.close()
    return response


@app.post(
    "/api/organisations/{orgId}/users",
    response_model=UserOrganizationSchemaResponse,
)
def add_user_to_organisation(
    orgId: str, user: UserOrganizationSchema, db: Session = Depends(get_db)
):
    org = db.query(Organization).filter(Organization.orgId == orgId).first()
    if not org:
        content = {
            "status": "Bad Request",
            "message": "organization not found",
            "statusCode": 404,
        }
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content=content
        )
    user_exist = db.query(User).filter(User.userId == user.userId).first()
    if not user_exist:
        content = {
            "status": "Bad Request",
            "message": "user not found",
            "statusCode": 404,
        }
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content=content
        )

    org.users.append(user_exist)
    db.commit()
    response = UserOrganizationSchemaResponse(
        status="success", message="User added to organisation successfully"
    )
    db.close()
    return response


@app.exception_handler(RequestValidationError)
def custom_request_validation_error(
    request: Request, exc: RequestValidationError
):
    """
    handles the user validation error response
    """
    error = [
        {"fields": err["loc"][0], "message": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"errors": error},
    )
