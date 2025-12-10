"""
Quick verification script to check if all authentication components are properly implemented
"""
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} NOT FOUND")
        return False

def check_imports():
    """Check if all required modules can be imported"""
    print("\n=== Checking Python Imports ===")

    try:
        from app.models.database import User
        print("✅ User model imported successfully")

        # Check if new fields exist
        from sqlalchemy import inspect
        inspector = inspect(User)
        columns = [col.name for col in inspector.columns]

        required_fields = ['password_hash', 'role', 'cv_text', 'availability_date',
                          'public_profile', 'willing_to_relocate', 'company_name',
                          'company_url', 'recruiter_type']

        for field in required_fields:
            if field in columns:
                print(f"  ✅ Field '{field}' exists in User model")
            else:
                print(f"  ❌ Field '{field}' MISSING in User model")

    except Exception as e:
        print(f"❌ Error importing User model: {str(e)}")
        return False

    try:
        from app.routes import auth
        print("✅ Auth routes module imported successfully")
    except Exception as e:
        print(f"❌ Error importing auth routes: {str(e)}")
        return False

    try:
        from app.middleware.auth import get_current_user, require_admin
        print("✅ Auth middleware imported successfully")
    except Exception as e:
        print(f"❌ Error importing auth middleware: {str(e)}")
        return False

    try:
        from passlib.context import CryptContext
        print("✅ Passlib (bcrypt) imported successfully")
    except Exception as e:
        print(f"❌ Error importing passlib: {str(e)}")
        return False

    try:
        from jose import jwt
        print("✅ Python-jose (JWT) imported successfully")
    except Exception as e:
        print(f"❌ Error importing jose: {str(e)}")
        return False

    return True

def main():
    print("=" * 60)
    print("AUTHENTICATION SYSTEM IMPLEMENTATION VERIFICATION")
    print("=" * 60)

    # Check backend files
    print("\n=== Checking Backend Files ===")
    backend_files = [
        ("backend/app/models/database.py", "User model (updated)"),
        ("backend/app/routes/auth.py", "Auth routes"),
        ("backend/app/middleware/auth.py", "Auth middleware"),
        ("backend/app/middleware/__init__.py", "Middleware package"),
        ("backend/app/config/settings.py", "Settings (with JWT config)"),
        ("backend/requirements.txt", "Requirements (with auth deps)"),
    ]

    for filepath, desc in backend_files:
        check_file_exists(filepath, desc)

    # Check frontend files
    print("\n=== Checking Frontend Files ===")
    frontend_files = [
        ("frontend/src/services/auth.js", "Auth service"),
        ("frontend/src/components/Auth/Login.jsx", "Login component"),
        ("frontend/src/components/Auth/Register.jsx", "Register component"),
        ("frontend/src/styles/Auth.css", "Auth styles"),
    ]

    for filepath, desc in frontend_files:
        check_file_exists(filepath, desc)

    # Check imports
    check_imports()

    print("\n=== Configuration Check ===")
    try:
        from app.config.settings import settings
        print(f"✅ JWT_SECRET_KEY configured: {'*' * len(settings.JWT_SECRET_KEY)}")
        print(f"✅ JWT_ALGORITHM: {settings.JWT_ALGORITHM}")
        print(f"✅ JWT_EXPIRATION_HOURS: {settings.JWT_EXPIRATION_HOURS}")
    except Exception as e:
        print(f"❌ Error checking settings: {str(e)}")

    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETED")
    print("=" * 60)
    print("\nTo test the system:")
    print("1. Start backend: cd backend && python -m uvicorn app.main:app --reload")
    print("2. Visit: http://localhost:8000/docs")
    print("3. Test endpoints: /auth/register and /auth/login")
    print("\nOr run: python test_auth.py (with backend running)")

if __name__ == "__main__":
    main()
