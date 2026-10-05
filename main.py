from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import User, Profile

from schemas import (
    UserRegister,
    UserLogin,
    ProfileCreate,
    RegisterResponse,
    LoginResponse,
    ProfileResponse,
    UserResponse
)

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

# import models


app = FastAPI(
    title="User Management System API",
    description="""
# User Management System

REST API for user registration, authentication and profile management.

## Features

- User registration
- User login
- JWT authentication
- Create user profile
- View own profile
- Update own profile
- Delete own profile
- Get all users

## Authentication

Protected APIs require a JWT token.

Use the **Authorize** button in Swagger UI and enter:

`Bearer <your_access_token>`
""",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User registration and login APIs"
        },
        {
            "name": "Users",
            "description": "User management APIs"
        },
        {
            "name": "Profile",
            "description": "Create and manage user profiles"
        },
        {
            "name": "Testing",
            "description": "Authentication testing APIs"
        }
    ]
)


Base.metadata.create_all(bind=engine)


# =====================================================
# HOME
# =====================================================

@app.get(
    "/",
    summary="Check API status",
    description="Returns the current status of the User Management System API."
)
def home():

    return {
        "message": "User Management System API is running"
    }


# =====================================================
# REGISTER
# =====================================================

@app.post(
    "/auth/register",
    response_model=RegisterResponse,
    tags=["Authentication"],
    summary="Register a new user",
    description="""
Creates a new user account.

The password is securely hashed before being stored in the database.

### Validation

- Name must contain at least 2 characters
- Email must be a valid email address
- Password must contain at least 6 characters
""",
    responses={
        400: {
            "description": "Email already registered"
        },
        422: {
            "description": "Validation error"
        }
    }
)
def register(
    user: UserRegister,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }


# =====================================================
# LOGIN
# =====================================================

@app.post(
    "/auth/login",
    response_model=LoginResponse,
    tags=["Authentication"],
    summary="Login user",
    description="""
Authenticates a user using email and password.

If authentication is successful, a JWT access token is returned.

Use this token to access protected APIs.
""",
    responses={
        401: {
            "description": "Invalid email or password"
        },
        422: {
            "description": "Validation error"
        }
    }
)
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email"
        )

    if not verify_password(
        user.password,
        existing_user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    access_token = create_access_token(
        existing_user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# =====================================================
# TEST AUTHENTICATION
# =====================================================

@app.get(
    "/test-auth",
    tags=["Testing"],
    summary="Test JWT authentication",
    description="""
Tests whether the supplied JWT access token is valid.

This endpoint requires authentication.
""",
    responses={
        401: {
            "description": "Missing or invalid authentication token"
        }
    }
)
def test_auth(
    user_id: int = Depends(get_current_user)
):

    return {
        "message": "Authentication successful",
        "user_id": user_id
    }


# =====================================================
# CREATE PROFILE
# =====================================================

@app.post(
    "/users/profile",
    tags=["Profile"],
    response_model=dict,
    summary="Create my profile",
    description="""
Creates a profile for the currently authenticated user.

A user can have only one profile.
""",
    responses={
        400: {
            "description": "Profile already exists"
        },
        401: {
            "description": "Authentication required"
        }
    }
)
def create_profile(
    profile: ProfileCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    existing_profile = db.query(Profile).filter(
        Profile.user_id == user_id
    ).first()

    if existing_profile:

        raise HTTPException(
            status_code=400,
            detail="Profile already exists"
        )

    new_profile = Profile(
        user_id=user_id,
        phone=profile.phone,
        address=profile.address,
        date_of_birth=profile.date_of_birth,
        bio=profile.bio
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return {
        "message": "Profile created successfully",
        "profile_id": new_profile.id
    }


# =====================================================
# GET MY PROFILE
# =====================================================

@app.get(
    "/users/me",
    response_model=ProfileResponse,
    tags=["Profile"],
    summary="Get my profile",
    description="""
Returns the profile of the currently authenticated user.
""",
    responses={
        401: {
            "description": "Authentication required"
        },
        404: {
            "description": "Profile not found"
        }
    }
)
def get_my_profile(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    profile = db.query(Profile).filter(
        Profile.user_id == user_id
    ).first()

    if not profile:

        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "phone": profile.phone,
        "address": profile.address,
        "date_of_birth": profile.date_of_birth,
        "bio": profile.bio
    }


# =====================================================
# GET ALL USERS
# =====================================================

@app.get(
    "/users",
    response_model=list[UserResponse],
    tags=["Users"],
    summary="Get all users",
    description="""
Returns a list of all registered users.

Passwords are never returned.
""",
    responses={
        401: {
            "description": "Authentication required"
        }
    }
)
def get_users(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
        for user in users
    ]


# =====================================================
# UPDATE PROFILE
# =====================================================

@app.put(
    "/users/profile",
    tags=["Profile"],
    summary="Update my profile",
    description="""
Updates the profile of the currently authenticated user.
""",
    responses={
        401: {
            "description": "Authentication required"
        },
        404: {
            "description": "Profile not found"
        }
    }
)
def update_profile(
    profile_data: ProfileCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    profile = db.query(Profile).filter(
        Profile.user_id == user_id
    ).first()

    if not profile:

        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    profile.phone = profile_data.phone
    profile.address = profile_data.address
    profile.date_of_birth = profile_data.date_of_birth
    profile.bio = profile_data.bio

    db.commit()
    db.refresh(profile)

    return {
        "message": "Profile updated successfully"
    }


# =====================================================
# DELETE PROFILE
# =====================================================

@app.delete(
    "/users/profile",
    tags=["Profile"],
    summary="Delete my profile",
    description="""
Deletes the profile belonging to the currently authenticated user.
""",
    responses={
        401: {
            "description": "Authentication required"
        },
        404: {
            "description": "Profile not found"
        }
    }
)
def delete_profile(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    profile = db.query(Profile).filter(
        Profile.user_id == user_id
    ).first()

    if not profile:

        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    db.delete(profile)
    db.commit()

    return {
        "message": "Profile deleted successfully"
    }