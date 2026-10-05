from pydantic import BaseModel, EmailStr, Field
from datetime import date



class UserRegister(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the user",
        examples=["Unni"]
    )

    email: EmailStr = Field(
        ...,
        description="User email address",
        examples=["unni@gmail.com"]
    )

    password: str = Field(
        ...,
        min_length=6,
        description="User password. Minimum 6 characters",
        examples=["123456"]
    )


class UserLogin(BaseModel):
    email: EmailStr = Field(
        ...,
        description="Registered email address",
        examples=["unni@gmail.com"]
    )

    password: str = Field(
        ...,
        min_length=6,
        description="User password",
        examples=["123456"]
    )


class ProfileCreate(BaseModel):
    phone: str = Field(
        ...,
        description="User phone number",
        examples=["9876543210"]
    )

    address: str = Field(
        ...,
        description="User residential address",
        examples=["Chennai, Tamil Nadu"]
    )

    date_of_birth: date = Field(
        ...,
        description="User date of birth",
        examples=["1998-05-20"]
    )

    bio: str | None = Field(
        default=None,
        max_length=500,
        description="Short biography",
        examples=["Software Engineer"]
    )




class RegisterResponse(BaseModel):
    message: str
    user_id: int


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    phone: str
    address: str
    date_of_birth: date
    bio: str | None


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr