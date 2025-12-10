"""
Authentication middleware for JWT validation and role-based access control
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional
from functools import wraps

from app.models.database import User, get_db
from app.config.settings import settings

security = HTTPBearer()


def decode_token(token: str) -> dict:
    """
    Decode and validate JWT token
    Returns payload dict with user_id (sub) and role
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token

    Usage in routes:
        @router.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.user_id, "role": current_user.role}
    """
    token = credentials.credentials
    payload = decode_token(token)

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Fetch user from database
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication - returns None if no token provided
    Useful for routes that work both authenticated and unauthenticated

    Usage:
        @router.get("/public-or-private")
        async def route(user: Optional[User] = Depends(get_current_user_optional)):
            if user:
                return {"message": f"Hello {user.name}"}
            return {"message": "Hello guest"}
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = decode_token(token)
        user_id: str = payload.get("sub")

        if user_id:
            user = db.query(User).filter(User.user_id == user_id).first()
            return user
    except HTTPException:
        pass

    return None


class RoleChecker:
    """
    Dependency class for role-based access control

    Usage:
        require_admin = RoleChecker(["admin"])
        require_recruiter = RoleChecker(["recruiter", "admin"])

        @router.get("/admin-only")
        async def admin_route(current_user: User = Depends(require_admin)):
            return {"message": "Admin access granted"}
    """
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden. Required roles: {', '.join(self.allowed_roles)}"
            )
        return current_user


# Pre-defined role checkers for convenience
require_admin = RoleChecker(["admin"])
require_recruiter = RoleChecker(["recruiter", "admin"])
require_candidate = RoleChecker(["candidate", "admin"])
require_any_authenticated = RoleChecker(["candidate", "recruiter", "admin"])


def require_role(*roles: str):
    """
    Decorator for route functions to enforce role-based access

    Usage:
        @router.get("/recruiter-dashboard")
        @require_role("recruiter", "admin")
        async def dashboard(current_user: User = Depends(get_current_user)):
            return {"message": "Welcome to recruiter dashboard"}

    Note: The route function must have current_user parameter with Depends(get_current_user)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User, **kwargs):
            if current_user.role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access forbidden. Required roles: {', '.join(roles)}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
