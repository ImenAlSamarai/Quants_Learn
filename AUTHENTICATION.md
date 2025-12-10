# Multi-Role Authentication System

## Overview

Complete authentication system with JWT-based authentication and role-based access control. Supports three user roles: **Candidate**, **Recruiter**, and **Admin**.

## Features

- User registration with role selection
- Secure password hashing with bcrypt (cost factor 12)
- JWT token-based authentication (24-hour expiration)
- Role-based access control
- Role-specific user fields (candidate and recruiter profiles)
- Frontend authentication components (Login/Register)

---

## Backend Implementation

### 1. Database Schema

**New User fields** (added to `backend/app/models/database.py`):

#### Authentication Fields
- `password_hash` (String 255) - Bcrypt hashed password
- `role` (String 50) - User role: 'candidate', 'recruiter', 'admin'

#### Candidate-Specific Fields (nullable)
- `cv_text` (Text) - Resume/CV content
- `availability_date` (Date) - When candidate is available
- `public_profile` (Boolean, default: False) - Profile visibility
- `willing_to_relocate` (Boolean) - Relocation preference

#### Recruiter-Specific Fields (nullable)
- `company_name` (String 200) - Recruiter's company
- `company_url` (String 500) - Company website
- `recruiter_type` (String 50) - 'internal', 'agency', 'headhunter'

### 2. API Endpoints

#### Register: `POST /auth/register`

Create a new user account with role selection.

**Request Body:**
```json
{
  "user_id": "username_or_email",
  "password": "min_8_characters",
  "name": "Full Name",
  "email": "user@example.com",
  "role": "candidate",  // or "recruiter", "admin"

  // Candidate-specific (optional)
  "cv_text": "Resume content...",
  "availability_date": "2024-01-01",
  "willing_to_relocate": true,

  // Recruiter-specific (optional)
  "company_name": "Company LLC",
  "company_url": "https://company.com",
  "recruiter_type": "internal"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": "username_or_email",
  "role": "candidate",
  "name": "Full Name"
}
```

#### Login: `POST /auth/login`

Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "user_id": "username_or_email",
  "password": "user_password"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": "username_or_email",
  "role": "candidate",
  "name": "Full Name"
}
```

#### Logout: `POST /auth/logout`

Client-side token deletion (JWT tokens are stateless).

**Response (200 OK):**
```json
{
  "message": "Logged out successfully. Please delete your token client-side."
}
```

### 3. Authentication Middleware

Location: `backend/app/middleware/auth.py`

#### Get Current User

```python
from app.middleware.auth import get_current_user

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.user_id, "role": current_user.role}
```

#### Role-Based Access Control

```python
from app.middleware.auth import require_admin, require_recruiter, RoleChecker

# Pre-defined role checkers
@router.get("/admin-only")
async def admin_route(current_user: User = Depends(require_admin)):
    return {"message": "Admin access granted"}

# Custom role checker
require_recruiter_or_admin = RoleChecker(["recruiter", "admin"])

@router.get("/recruiter-dashboard")
async def dashboard(current_user: User = Depends(require_recruiter_or_admin)):
    return {"message": "Recruiter dashboard"}
```

#### Optional Authentication

```python
from app.middleware.auth import get_current_user_optional

@router.get("/public-or-private")
async def route(user: Optional[User] = Depends(get_current_user_optional)):
    if user:
        return {"message": f"Hello {user.name}"}
    return {"message": "Hello guest"}
```

### 4. JWT Configuration

Location: `backend/app/config/settings.py`

```python
JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRATION_HOURS: int = 24
```

**Important:** Change `JWT_SECRET_KEY` in production!

### 5. Security Features

- **Password Hashing:** Bcrypt with cost factor 12
- **JWT Expiration:** 24 hours
- **Role in Payload:** Role included in JWT for efficient authorization
- **Public Profile Default:** False (privacy-first)
- **Password Validation:** Minimum 8 characters

---

## Frontend Implementation

### 1. Authentication Service

Location: `frontend/src/services/auth.js`

#### Register

```javascript
import { register } from '../../services/auth';

const registrationData = {
  user_id: "username",
  password: "password123",
  name: "Full Name",
  email: "user@example.com",
  role: "candidate",
  // Optional role-specific fields...
};

const response = await register(registrationData);
// Token is automatically stored in localStorage
```

#### Login

```javascript
import { login } from '../../services/auth';

const response = await login("username", "password");
// Token is automatically stored in localStorage
```

#### Logout

```javascript
import { logout } from '../../services/auth';

await logout();
// Token is automatically removed from localStorage
```

#### Check Authentication

```javascript
import { isAuthenticated, getUser, getRole, hasRole } from '../../services/auth';

if (isAuthenticated()) {
  const user = getUser(); // { user_id, role, name }
  const role = getRole(); // "candidate" | "recruiter" | "admin"

  if (hasRole("admin")) {
    // Admin-specific logic
  }
}
```

### 2. React Components

#### Login Component

Location: `frontend/src/components/Auth/Login.jsx`

```javascript
import Login from './components/Auth/Login';

<Login
  onSuccess={(response) => {
    console.log('Login successful:', response);
    // Redirect or update UI
  }}
  onSwitchToRegister={() => {
    // Switch to registration view
  }}
/>
```

#### Register Component

Location: `frontend/src/components/Auth/Register.jsx`

```javascript
import Register from './components/Auth/Register';

<Register
  onSuccess={(response) => {
    console.log('Registration successful:', response);
    // Redirect or update UI
  }}
  onSwitchToLogin={() => {
    // Switch to login view
  }}
/>
```

### 3. Automatic Token Management

The auth service automatically:
- Stores JWT token in `localStorage` on login/register
- Adds `Authorization: Bearer <token>` header to all API requests
- Removes token on logout
- Redirects to login on 401 (token expiration)

---

## Database Migration

Run the migration script to add new fields to existing database:

```bash
cd backend
python migrate_auth.py
```

This adds:
- Authentication fields (password_hash, role)
- Candidate-specific fields
- Recruiter-specific fields

**Note:** Existing users will have NULL password_hash and need to re-register.

---

## Testing

### Backend Tests

1. Start the backend server:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

2. Run authentication tests:
```bash
cd backend
python test_auth.py
```

3. Or test via Swagger UI:
   - Visit: http://localhost:8000/docs
   - Try `/auth/register` and `/auth/login` endpoints

### Verification Script

```bash
cd backend
python verify_implementation.py
```

This checks:
- All files are created
- Database fields exist
- Dependencies are installed
- Configuration is correct

---

## API Documentation

Full interactive API documentation available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Security Best Practices

1. **Change JWT Secret:** Update `JWT_SECRET_KEY` in production
2. **Use HTTPS:** Always use HTTPS in production
3. **Token Storage:** Tokens stored in localStorage (consider httpOnly cookies for extra security)
4. **Password Requirements:** Enforce strong passwords (current min: 8 chars)
5. **Rate Limiting:** Consider adding rate limiting for auth endpoints
6. **Email Verification:** Consider adding email verification for production

---

## User Roles

### Candidate
- Job seekers
- Access to learning platform
- Can create public profiles
- Can upload CVs and set availability

### Recruiter
- Hiring managers and recruiters
- Can search for candidates
- Company affiliation required
- Access to candidate database

### Admin
- Platform administrators
- Full access to all features
- Can manage users and content

---

## Files Modified/Created

### Backend
- ✅ `app/models/database.py` - Added auth fields to User model
- ✅ `app/routes/auth.py` - Authentication routes
- ✅ `app/middleware/auth.py` - JWT validation and role checking
- ✅ `app/middleware/__init__.py` - Middleware package
- ✅ `app/config/settings.py` - JWT configuration
- ✅ `app/main.py` - Registered auth routes
- ✅ `requirements.txt` - Added auth dependencies
- ✅ `migrate_auth.py` - Database migration script
- ✅ `test_auth.py` - Authentication test suite
- ✅ `verify_implementation.py` - Implementation verification

### Frontend
- ✅ `src/services/auth.js` - Authentication service
- ✅ `src/components/Auth/Login.jsx` - Login component
- ✅ `src/components/Auth/Register.jsx` - Register component
- ✅ `src/styles/Auth.css` - Authentication styles

---

## Dependencies Added

```txt
python-jose[cryptography]==3.3.0  # JWT handling
passlib[bcrypt]==1.7.4            # Password hashing
email-validator==2.3.0            # Email validation
```

---

## Next Steps (Optional Enhancements)

1. Add password reset functionality
2. Implement email verification
3. Add OAuth2 providers (Google, LinkedIn)
4. Add two-factor authentication
5. Implement refresh tokens
6. Add password strength requirements
7. Add rate limiting for auth endpoints
8. Add user profile management UI
9. Add admin panel for user management
10. Add activity logging and audit trail

---

## Support

For issues or questions:
1. Check API docs: http://localhost:8000/docs
2. Run verification: `python verify_implementation.py`
3. Check logs in backend console
4. Review this documentation

---

**Status:** ✅ Implementation Complete - Ready for Testing
