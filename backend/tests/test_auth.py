"""
Authentication tests for ExamSaaS platform.
Tests cover registration, login, token refresh, and OTP verification.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from bson import ObjectId


class TestAuthRegister:
    """Test cases for user registration."""
    
    def test_register_success(self, client, test_db, mock_celery_task):
        """Test successful user registration."""
        response = client.post('/api/v1/auth/register', json={
            "email": "newuser@test.com",
            "password": "SecurePass123!",
            "first_name": "New",
            "last_name": "User"
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert "OTP sent" in data["message"]
        assert "user_id" in data["data"]
        
        user = test_db.users.find_one({"email": "newuser@test.com"})
        assert user is not None
        assert user["first_name"] == "New"
        assert user["is_email_verified"] is False
    
    def test_register_duplicate_email(self, client, test_db, test_user_student, mock_celery_task):
        """Test registration with existing email fails."""
        response = client.post('/api/v1/auth/register', json={
            "email": test_user_student["email"],
            "password": "SecurePass123!",
            "first_name": "Duplicate",
            "last_name": "User"
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert data["success"] is False
        assert "already exists" in data["message"].lower()
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        response = client.post('/api/v1/auth/register', json={
            "email": "not-an-email",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False
        assert "validation" in data["message"].lower() or "email" in str(data.get("errors", {})).lower()
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields."""
        response = client.post('/api/v1/auth/register', json={
            "email": "test@test.com"
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False
    
    def test_register_weak_password(self, client):
        """Test registration with weak password fails."""
        response = client.post('/api/v1/auth/register', json={
            "email": "test@test.com",
            "password": "weak",
            "first_name": "Test",
            "last_name": "User"
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False
    
    def test_register_short_first_name(self, client):
        """Test registration with too short first name fails."""
        response = client.post('/api/v1/auth/register', json={
            "email": "test@test.com",
            "password": "SecurePass123!",
            "first_name": "A",
            "last_name": "User"
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False


class TestAuthLogin:
    """Test cases for user login."""
    
    def test_login_success(self, client, test_db, test_user_student):
        """Test successful login returns tokens."""
        test_db.users.update_one(
            {"email": test_user_student["email"]},
            {"$set": {"is_email_verified": True}}
        )
        
        response = client.post('/api/v1/auth/login', json={
            "email": test_user_student["email"],
            "password": test_user_student["password"]
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["user"]["email"] == test_user_student["email"]
    
    def test_login_wrong_password(self, client, test_db, test_user_student):
        """Test login with wrong password fails."""
        test_db.users.update_one(
            {"email": test_user_student["email"]},
            {"$set": {"is_email_verified": True}}
        )
        
        response = client.post('/api/v1/auth/login', json={
            "email": test_user_student["email"],
            "password": "WrongPassword123!"
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False
        assert "invalid" in data["message"].lower() or "credential" in data["message"].lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email fails."""
        response = client.post('/api/v1/auth/login', json={
            "email": "nonexistent@test.com",
            "password": "SomePassword123!"
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False
    
    def test_login_suspended_institute(self, client, test_db, suspended_institute_user):
        """Test login blocked for user of suspended institute."""
        response = client.post('/api/v1/auth/login', json={
            "email": suspended_institute_user["email"],
            "password": suspended_institute_user["password"]
        })
        
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False
        assert "suspended" in data["message"].lower()
    
    def test_login_unverified_email(self, client, test_db, test_user_student):
        """Test login blocked for unverified email."""
        test_db.users.update_one(
            {"email": test_user_student["email"]},
            {"$set": {"is_email_verified": False}}
        )
        
        response = client.post('/api/v1/auth/login', json={
            "email": test_user_student["email"],
            "password": test_user_student["password"]
        })
        
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False
        assert "verified" in data["message"].lower()
    
    def test_login_inactive_user(self, client, test_db, test_user_student):
        """Test login blocked for inactive user."""
        test_db.users.update_one(
            {"email": test_user_student["email"]},
            {"$set": {"is_active": False}}
        )
        
        response = client.post('/api/v1/auth/login', json={
            "email": test_user_student["email"],
            "password": test_user_student["password"]
        })
        
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields fails."""
        response = client.post('/api/v1/auth/login', json={
            "email": "test@test.com"
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False


class TestAuthRefresh:
    """Test cases for token refresh."""
    
    def test_refresh_token_success(self, client, test_db, test_user_student):
        """Test successful token refresh."""
        test_db.users.update_one(
            {"email": test_user_student["email"]},
            {"$set": {"is_email_verified": True}}
        )
        
        login_response = client.post('/api/v1/auth/login', json={
            "email": test_user_student["email"],
            "password": test_user_student["password"]
        })
        refresh_token = login_response.get_json()["data"]["refresh_token"]
        
        response = client.post('/api/v1/auth/refresh', json={
            "refresh_token": refresh_token
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
    
    def test_refresh_invalid_token(self, client):
        """Test refresh with invalid token fails."""
        response = client.post('/api/v1/auth/refresh', json={
            "refresh_token": "invalid_token_here"
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False
    
    def test_refresh_expired_token(self, client, test_db, test_user_student):
        """Test refresh with expired token fails."""
        with patch('flask_jwt_extended.utils.get_jwt') as mock_jwt:
            mock_jwt.return_value = {
                "exp": datetime.utcnow() - timedelta(hours=1),
                "iat": datetime.utcnow() - timedelta(hours=2),
                "sub": test_user_student["id"],
                "jti": "test_jti",
                "type": "refresh"
            }
            
            response = client.post('/api/v1/auth/refresh', json={
                "refresh_token": "expired_token"
            })
            
            assert response.status_code == 401
            data = response.get_json()
            assert data["success"] is False
    
    def test_refresh_missing_token(self, client):
        """Test refresh without token fails."""
        response = client.post('/api/v1/auth/refresh', json={})
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False


class TestAuthOTP:
    """Test cases for OTP verification."""
    
    def test_send_otp(self, client, test_db, test_user_student, mock_celery_task):
        """Test OTP sending to user email."""
        response = client.post('/api/v1/auth/resend-otp', json={
            "email": test_user_student["email"],
            "purpose": "verify_email"
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "sent" in data["message"].lower()
    
    def test_verify_otp_success(self, client, test_db, test_user_student):
        """Test successful OTP verification."""
        test_db.otps.insert_one({
            "email": test_user_student["email"],
            "otp": "123456",
            "purpose": "verify_email",
            "expires_at": datetime.utcnow() + timedelta(minutes=10),
            "attempts": 0,
            "created_at": datetime.utcnow(),
        })
        
        response = client.post('/api/v1/auth/verify-email', json={
            "email": test_user_student["email"],
            "otp": "123456"
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        
        user = test_db.users.find_one({"email": test_user_student["email"]})
        assert user["is_email_verified"] is True
    
    def test_verify_otp_wrong_code(self, client, test_db, test_user_student):
        """Test OTP verification with wrong code fails."""
        test_db.otps.insert_one({
            "email": test_user_student["email"],
            "otp": "123456",
            "purpose": "verify_email",
            "expires_at": datetime.utcnow() + timedelta(minutes=10),
            "attempts": 0,
            "created_at": datetime.utcnow(),
        })
        
        response = client.post('/api/v1/auth/verify-email', json={
            "email": test_user_student["email"],
            "otp": "000000"
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
    
    def test_verify_otp_expired(self, client, test_db, test_user_student):
        """Test OTP verification with expired code fails."""
        test_db.otps.insert_one({
            "email": test_user_student["email"],
            "otp": "123456",
            "purpose": "verify_email",
            "expires_at": datetime.utcnow() - timedelta(minutes=1),
            "attempts": 0,
            "created_at": datetime.utcnow() - timedelta(minutes=15),
        })
        
        response = client.post('/api/v1/auth/verify-email', json={
            "email": test_user_student["email"],
            "otp": "123456"
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
    
    def test_verify_otp_nonexistent_user(self, client):
        """Test OTP verification for non-existent user fails."""
        response = client.post('/api/v1/auth/verify-email', json={
            "email": "nonexistent@test.com",
            "otp": "123456"
        })
        
        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False


class TestAuthLogout:
    """Test cases for user logout."""
    
    def test_logout_success(self, client, test_db, test_user_student):
        """Test successful logout."""
        test_db.users.update_one(
            {"email": test_user_student["email"]},
            {"$set": {"is_email_verified": True}}
        )
        
        login_response = client.post('/api/v1/auth/login', json={
            "email": test_user_student["email"],
            "password": test_user_student["password"]
        })
        access_token = login_response.get_json()["data"]["access_token"]
        
        response = client.post('/api/v1/auth/logout', headers={
            "Authorization": f"Bearer {access_token}"
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
    
    def test_logout_without_token(self, client):
        """Test logout without token fails."""
        response = client.post('/api/v1/auth/logout')
        
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False


class TestAuthProfile:
    """Test cases for user profile management."""
    
    def test_get_profile(self, client, test_db, test_user_student, auth_headers_student):
        """Test getting current user profile."""
        response = client.get('/api/v1/auth/me', headers=auth_headers_student)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["email"] == test_user_student["email"]
    
    def test_update_profile(self, client, test_db, test_user_student, auth_headers_student):
        """Test updating user profile."""
        response = client.patch('/api/v1/auth/me', 
            headers=auth_headers_student,
            json={
                "first_name": "Updated",
                "phone": "+1234567890"
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["first_name"] == "Updated"
        
        user = test_db.users.find_one({"email": test_user_student["email"]})
        assert user["first_name"] == "Updated"
    
    def test_get_profile_unauthorized(self, client):
        """Test getting profile without auth fails."""
        response = client.get('/api/v1/auth/me')
        
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False


class TestAuthForgotPassword:
    """Test cases for password reset functionality."""
    
    def test_forgot_password_success(self, client, test_db, test_user_student, mock_celery_task):
        """Test forgot password request succeeds."""
        response = client.post('/api/v1/auth/forgot-password', json={
            "email": test_user_student["email"]
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        
        otp = test_db.otps.find_one({
            "email": test_user_student["email"],
            "purpose": "forgot_password"
        })
        assert otp is not None
    
    def test_forgot_password_nonexistent_user(self, client):
        """Test forgot password for non-existent user returns success (security)."""
        response = client.post('/api/v1/auth/forgot-password', json={
            "email": "nonexistent@test.com"
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
    
    def test_reset_password_success(self, client, test_db, test_user_student):
        """Test successful password reset."""
        test_db.otps.insert_one({
            "email": test_user_student["email"],
            "otp": "654321",
            "purpose": "forgot_password",
            "expires_at": datetime.utcnow() + timedelta(minutes=10),
            "attempts": 0,
            "created_at": datetime.utcnow(),
        })
        
        response = client.post('/api/v1/auth/reset-password', json={
            "email": test_user_student["email"],
            "otp": "654321",
            "new_password": "NewSecurePass123!"
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        
        user = test_db.users.find_one({"email": test_user_student["email"]})
        assert user["password_hash"] != test_user_student.get("password_hash")
