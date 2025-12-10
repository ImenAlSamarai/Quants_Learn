"""
Authentication routes for user registration and login
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext

from app.models.database import User, get_db
from app.config.settings import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Password hashing with bcrypt (cost factor 12)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


# Pydantic models
class UserRegistration(BaseModel):
    user_id: str = Field(..., min_length=3, max_length=100, description="Username or email")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: str = Field(default="candidate", pattern="^(candidate|recruiter|admin)$")

    # Candidate-specific fields
    cv_text: Optional[str] = None
    availability_date: Optional[str] = None  # ISO date string
    willing_to_relocate: Optional[bool] = None

    # Recruiter-specific fields
    company_name: Optional[str] = None
    company_url: Optional[str] = None
    recruiter_type: Optional[str] = Field(None, pattern="^(internal|agency|headhunter)?$")


class UserLogin(BaseModel):
    user_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    name: Optional[str] = None


# Helper functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt with cost factor 12"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, role: str) -> str:
    """Create JWT access token with user_id and role in payload"""
    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    to_encode = {
        "sub": user_id,
        "role": role,
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


# Routes
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(registration: UserRegistration, db: Session = Depends(get_db)):
    """
    Register a new user with role selection

    Roles:
    - candidate: Job seekers, learning platform users
    - recruiter: Recruiters looking for candidates
    - admin: Platform administrators
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.user_id == registration.user_id).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID already registered"
        )

    # Check if email is already registered (if provided)
    if registration.email:
        existing_email = db.query(User).filter(User.email == registration.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    # Hash password
    password_hash = hash_password(registration.password)

    # Create new user
    new_user = User(
        user_id=registration.user_id,
        password_hash=password_hash,
        name=registration.name,
        email=registration.email,
        role=registration.role,
        public_profile=False,  # Default to private
        created_at=datetime.utcnow(),
        last_active=datetime.utcnow()
    )

    # Add role-specific fields
    if registration.role == "candidate":
        new_user.cv_text = registration.cv_text
        if registration.availability_date:
            try:
                new_user.availability_date = datetime.fromisoformat(registration.availability_date).date()
            except ValueError:
                pass  # Ignore invalid date format
        new_user.willing_to_relocate = registration.willing_to_relocate

    elif registration.role == "recruiter":
        new_user.company_name = registration.company_name
        new_user.company_url = registration.company_url
        new_user.recruiter_type = registration.recruiter_type

    # Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT token
    access_token = create_access_token(new_user.user_id, new_user.role)

    return TokenResponse(
        access_token=access_token,
        user_id=new_user.user_id,
        role=new_user.role,
        name=new_user.name
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with user_id and password
    Returns JWT token with role in payload
    """
    # Find user
    user = db.query(User).filter(User.user_id == credentials.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Update last active
    user.last_active = datetime.utcnow()
    db.commit()

    # Generate JWT token
    access_token = create_access_token(user.user_id, user.role)

    return TokenResponse(
        access_token=access_token,
        user_id=user.user_id,
        role=user.role,
        name=user.name
    )


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client-side token deletion)
    JWT tokens are stateless, so logout is handled client-side by deleting the token
    """
    return {"message": "Logged out successfully. Please delete your token client-side."}
