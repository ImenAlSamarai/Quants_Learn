"""
Test script for authentication system
Tests registration, login, and JWT validation for both candidate and recruiter roles
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_registration():
    """Test user registration with candidate role"""
    print("\n=== Testing Candidate Registration ===")

    candidate_data = {
        "user_id": f"test_candidate_{datetime.now().timestamp()}",
        "password": "testpass123",
        "name": "Test Candidate",
        "email": f"candidate_{datetime.now().timestamp()}@test.com",
        "role": "candidate",
        "cv_text": "Experienced quantitative analyst with 3 years of experience",
        "availability_date": "2024-01-01",
        "willing_to_relocate": True
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=candidate_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 201:
            print("✅ Candidate registration successful!")
            return response.json()
        else:
            print("❌ Candidate registration failed!")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_recruiter_registration():
    """Test user registration with recruiter role"""
    print("\n=== Testing Recruiter Registration ===")

    recruiter_data = {
        "user_id": f"test_recruiter_{datetime.now().timestamp()}",
        "password": "testpass123",
        "name": "Test Recruiter",
        "email": f"recruiter_{datetime.now().timestamp()}@test.com",
        "role": "recruiter",
        "company_name": "Test Capital LLC",
        "company_url": "https://testcapital.com",
        "recruiter_type": "internal"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=recruiter_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 201:
            print("✅ Recruiter registration successful!")
            return response.json()
        else:
            print("❌ Recruiter registration failed!")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_login(user_id, password):
    """Test user login"""
    print(f"\n=== Testing Login for {user_id} ===")

    login_data = {
        "user_id": user_id,
        "password": password
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✅ Login successful!")
            return response.json()
        else:
            print("❌ Login failed!")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_protected_endpoint(token):
    """Test accessing a protected endpoint with JWT token"""
    print("\n=== Testing Protected Endpoint Access ===")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        # Try to access user profile endpoint (if it requires auth)
        response = requests.get(f"{BASE_URL}/api/users/demo_user", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code in [200, 404]:  # 404 is ok, means endpoint works but user not found
            print("✅ Protected endpoint access successful!")
            return True
        else:
            print("❌ Protected endpoint access failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_invalid_credentials():
    """Test login with invalid credentials"""
    print("\n=== Testing Invalid Credentials ===")

    login_data = {
        "user_id": "nonexistent_user",
        "password": "wrongpassword"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Status: {response.status_code}")

        if response.status_code == 401:
            print("✅ Invalid credentials correctly rejected!")
            return True
        else:
            print("❌ Invalid credentials not handled correctly!")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def run_all_tests():
    """Run all authentication tests"""
    print("=" * 60)
    print("AUTHENTICATION SYSTEM TEST SUITE")
    print("=" * 60)

    # Test 1: Register candidate
    candidate_result = test_registration()
    if not candidate_result:
        print("\n❌ Candidate registration failed. Stopping tests.")
        return

    # Test 2: Register recruiter
    recruiter_result = test_recruiter_registration()
    if not recruiter_result:
        print("\n❌ Recruiter registration failed. Stopping tests.")
        return

    # Test 3: Login candidate
    candidate_login = test_login(candidate_result['user_id'], "testpass123")
    if not candidate_login:
        print("\n❌ Candidate login failed.")

    # Test 4: Login recruiter
    recruiter_login = test_login(recruiter_result['user_id'], "testpass123")
    if not recruiter_login:
        print("\n❌ Recruiter login failed.")

    # Test 5: Test protected endpoint access
    if candidate_login:
        test_protected_endpoint(candidate_login['access_token'])

    # Test 6: Test invalid credentials
    test_invalid_credentials()

    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    print("Make sure the backend server is running on http://localhost:8000")
    print("Starting tests in 3 seconds...\n")

    import time
    time.sleep(3)

    run_all_tests()
