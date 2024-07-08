# from email_validator import validate_email, EmailNotValidError
from typing import Dict, List, Mapping, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    field_validator,
    model_validator,
)

from .validators import validate_field


class UserBaseSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str


class UserPostSchema(UserBaseSchema):
    password: str

    @field_validator("phone")
    @classmethod
    def validate_phone_number(cls, phone):
        pattern = r"\d+"
        msg = f"Invalid phone number {phone} provided, phone number can only be digit"
        phone = validate_field(phone, msg, pattern)
        return phone

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, first_name):
        pattern = r"^[^\d+$]+"
        msg = "first name can only contain alphabet and no numbers"
        first_name = validate_field(first_name, msg, pattern)
        return first_name

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, last_name):
        pattern = r"^[^\d+$]+"
        msg = "last name can only contain alphabet and no numbers"
        last_name = validate_field(last_name, msg, pattern)
        return last_name

    # @field_validator('email')
    # @classmethod
    # def email_validate(cls, values):
    #     try:
    #         email = validate_email(values)
    #     except EmailNotValidError as e:
    #         raise ValueError("Invalid email address provided")

    #     return values

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
