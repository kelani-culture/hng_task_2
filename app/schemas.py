# from email_validator import validate_email, EmailNotValidError
from typing import Dict, List, Mapping, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    field_validator,
    model_validator,
)

from app.validators import validate_field


class UserBaseSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str


class UserPostSchema(UserBaseSchema):
    password: str
    model_config = ConfigDict(from_attributes=True)


class UserDataSchema(BaseModel):
    userId: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: str


class UserData(BaseModel):
    access_token: str
    user: UserDataSchema


class UserResponseSchema(BaseModel):
    status: str
    message: str
    data: UserData


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserDetailSchema(BaseModel):
    status: str
    message: str
    data: UserDataSchema


# organization schema
class OrgBaseSchema(BaseModel):
    name: str
    description: Optional[str] = ""

    model_config = ConfigDict(from_attributes=True)


class OrgSchema(BaseModel):
    orgId: str
    name: str
    description: Optional[str] = ""


class OrgResponseSchema(BaseModel):
    status: str
    message: str
    data: OrgSchema


class UserOrgSchema(BaseModel):
    organisations: List[OrgSchema] = []


class UserOrgResponseSchema(BaseModel):
    status: str
    message: str
    data: UserOrgSchema


class UserOrganizationSchema(BaseModel):
    userId: str


class UserOrganizationSchemaResponse(BaseModel):
    status: str
    message: str
