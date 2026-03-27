"""
Test configuration and fixtures for ExamSaaS platform.
"""
import pytest
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
import mongomock
import fakeredis

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.config import Config


class TestConfig(Config):
    """Test configuration with in-memory defaults."""
    FLASK_ENV = "testing"
    TESTING = True
    DEBUG = False
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "test-jwt-secret"
    MONGO_URI = "mongodb://localhost:27017/examsaas_test"
    REDIS_URL = "redis://localhost:6379/15"
    CELERY_BROKER_URL = "redis://localhost:6379/14"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/13"
    CLOUDINARY_CLOUD_NAME = "test_cloud"
    CLOUDINARY_API_KEY = "test_key"
    CLOUDINARY_API_SECRET = "test_secret"
    RAZORPAY_KEY_ID = "test_razorpay_key"
    RAZORPAY_KEY_SECRET = "test_razorpay_secret"
    RAZORPAY_WEBHOOK_SECRET = "test_webhook_secret"
    GROQ_API_KEY = "test_groq_key"
    GROQ_MODEL = "llama-3.1-70b-versatile"


@pytest.fixture(scope="session")
def app():
    """Create application for testing."""
    config = TestConfig()
    
    with patch('app.extensions.PyMongo') as mock_pymongo:
        mock_mongo_client = mongomock.MongoClient()
        mock_pymongo_instance = MagicMock()
        mock_pymongo_instance.db = mock_mongo_client['examsaas_test']
        mock_pymongo_instance.cx = mock_mongo_client
        mock_pymongo.return_value = mock_pymongo_instance
        
        application = create_app(config)
        application.mongo_client = mock_mongo_client
        application.test_db = mock_mongo_client['examsaas_test']
        
        yield application


@pytest.fixture(scope="function")
def test_db(app):
    """Provide test database and clean it after each test."""
    db = app.test_db
    
    yield db
    
    for collection_name in db.list_collection_names():
        if collection_name.startswith('system.'):
            continue
        db[collection_name].delete_many({})


@pytest.fixture(scope="function")
def redis_client(app):
    """Provide mocked Redis client."""
    fake_redis = fakeredis.FakeRedis(decode_responses=True)
    
    yield fake_redis
    
    fake_redis.flushall()
    fake_redis.close()


@pytest.fixture(scope="function")
def client(app, test_db, redis_client):
    """Create test client with mocked dependencies."""
    app.test_db = test_db
    
    with patch('app.extensions.redis_client', redis_client):
        with patch('app.extensions.get_redis', return_value=redis_client):
            with app.test_client() as test_client:
                yield test_client


@pytest.fixture(scope="function")
def runner(app):
    """Create CLI runner."""
    return app.test_cli_runner()


@pytest.fixture(scope="function")
def test_user_superadmin(test_db):
    """Create super admin user."""
    user_data = {
        "email": "superadmin@test.com",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyDAHOEYT0A0Gm",
        "first_name": "Super",
        "last_name": "Admin",
        "role": "super_admin",
        "is_active": True,
        "is_email_verified": True,
        "auth_provider": "local",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = test_db.users.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    
    return {
        "id": str(user_data["_id"]),
        "email": user_data["email"],
        "password": "TestPass123!",
        "first_name": user_data["first_name"],
        "last_name": user_data["last_name"],
        "role": user_data["role"],
        "is_active": user_data["is_active"],
        "is_email_verified": user_data["is_email_verified"],
    }


@pytest.fixture(scope="function")
def test_user_admin(test_db):
    """Create college admin user."""
    institute_data = {
        "name": "Test College",
        "slug": "test-college-admin",
        "is_active": True,
        "is_suspended": False,
        "admin_type": "institute_admin",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    institute_result = test_db.institutes.insert_one(institute_data)
    institute_data["_id"] = institute_result.inserted_id
    
    user_data = {
        "email": "admin@testcollege.com",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyDAHOEYT0A0Gm",
        "first_name": "College",
        "last_name": "Admin",
        "role": "admin_college",
        "institute_id": institute_data["_id"],
        "is_active": True,
        "is_email_verified": True,
        "auth_provider": "local",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = test_db.users.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    
    wallet_data = {
        "user_id": user_data["_id"],
        "balance": 100000,
        "currency": "INR",
        "total_credited": 100000,
        "total_debited": 0,
        "version": 1,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    wallet_result = test_db.wallets.insert_one(wallet_data)
    wallet_data["_id"] = wallet_result.inserted_id
    
    return {
        "id": str(user_data["_id"]),
        "email": user_data["email"],
        "password": "TestPass123!",
        "first_name": user_data["first_name"],
        "last_name": user_data["last_name"],
        "role": user_data["role"],
        "institute_id": str(institute_data["_id"]),
        "wallet_id": str(wallet_data["_id"]),
        "is_active": user_data["is_active"],
        "is_email_verified": user_data["is_email_verified"],
        "institute": institute_data,
        "wallet": wallet_data,
    }


@pytest.fixture(scope="function")
def test_user_teacher(test_db, test_user_admin):
    """Create teacher user."""
    user_data = {
        "email": "teacher@testcollege.com",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyDAHOEYT0A0Gm",
        "first_name": "John",
        "last_name": "Teacher",
        "role": "teacher",
        "institute_id": test_user_admin["institute"]["_id"],
        "is_active": True,
        "is_email_verified": True,
        "auth_provider": "local",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = test_db.users.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    
    return {
        "id": str(user_data["_id"]),
        "email": user_data["email"],
        "password": "TestPass123!",
        "first_name": user_data["first_name"],
        "last_name": user_data["last_name"],
        "role": user_data["role"],
        "institute_id": test_user_admin["institute_id"],
        "is_active": user_data["is_active"],
        "is_email_verified": user_data["is_email_verified"],
    }


@pytest.fixture(scope="function")
def test_user_student(test_db, test_user_admin):
    """Create student user."""
    user_data = {
        "email": "student@testcollege.com",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyDAHOEYT0A0Gm",
        "first_name": "Jane",
        "last_name": "Student",
        "role": "student_registered",
        "institute_id": test_user_admin["institute"]["_id"],
        "is_active": True,
        "is_email_verified": True,
        "auth_provider": "local",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = test_db.users.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    
    wallet_data = {
        "user_id": user_data["_id"],
        "balance": 50000,
        "currency": "INR",
        "total_credited": 50000,
        "total_debited": 0,
        "version": 1,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    wallet_result = test_db.wallets.insert_one(wallet_data)
    wallet_data["_id"] = wallet_result.inserted_id
    
    return {
        "id": str(user_data["_id"]),
        "email": user_data["email"],
        "password": "TestPass123!",
        "first_name": user_data["first_name"],
        "last_name": user_data["last_name"],
        "role": user_data["role"],
        "institute_id": test_user_admin["institute_id"],
        "wallet_id": str(wallet_data["_id"]),
        "is_active": user_data["is_active"],
        "is_email_verified": user_data["is_email_verified"],
        "wallet": wallet_data,
    }


@pytest.fixture(scope="function")
def test_user_support(test_db):
    """Create support agent user."""
    user_data = {
        "email": "support@examsaas.com",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyDAHOEYT0A0Gm",
        "first_name": "Support",
        "last_name": "Agent",
        "role": "support_agent",
        "is_active": True,
        "is_email_verified": True,
        "auth_provider": "local",
        "support_scope": "platform",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = test_db.users.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    
    return {
        "id": str(user_data["_id"]),
        "email": user_data["email"],
        "password": "TestPass123!",
        "first_name": user_data["first_name"],
        "last_name": user_data["last_name"],
        "role": user_data["role"],
        "support_scope": user_data["support_scope"],
        "is_active": user_data["is_active"],
        "is_email_verified": user_data["is_email_verified"],
    }


@pytest.fixture(scope="function")
def suspended_institute_user(test_db):
    """Create user with suspended institute."""
    institute_data = {
        "name": "Suspended Institute",
        "slug": "suspended-institute",
        "is_active": True,
        "is_suspended": True,
        "admin_type": "institute_admin",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    institute_result = test_db.institutes.insert_one(institute_data)
    institute_data["_id"] = institute_result.inserted_id
    
    user_data = {
        "email": "suspended@testinstitute.com",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyDAHOEYT0A0Gm",
        "first_name": "Suspended",
        "last_name": "User",
        "role": "admin_college",
        "institute_id": institute_data["_id"],
        "is_active": True,
        "is_email_verified": True,
        "auth_provider": "local",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = test_db.users.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    
    return {
        "id": str(user_data["_id"]),
        "email": user_data["email"],
        "password": "TestPass123!",
        "role": user_data["role"],
        "institute_id": str(institute_data["_id"]),
        "is_suspended": True,
    }


def make_auth_headers(user, app):
    """Generate authorization headers with JWT token for a user."""
    from flask_jwt_extended import create_access_token, create_refresh_token
    
    with app.app_context():
        access_token = create_access_token(
            identity=user["id"],
            additional_claims={
                "email": user["email"],
                "role": user["role"],
            }
        )
        refresh_token = create_refresh_token(identity=user["id"])
    
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }, {
        "Authorization": f"Bearer {refresh_token}",
        "Content-Type": "application/json",
    }


@pytest.fixture(scope="function")
def auth_headers(app, test_user_admin):
    """Generate admin authorization headers."""
    access_headers, _ = make_auth_headers(test_user_admin, app)
    return access_headers


@pytest.fixture(scope="function")
def auth_headers_teacher(app, test_user_teacher):
    """Generate teacher authorization headers."""
    access_headers, _ = make_auth_headers(test_user_teacher, app)
    return access_headers


@pytest.fixture(scope="function")
def auth_headers_student(app, test_user_student):
    """Generate student authorization headers."""
    access_headers, _ = make_auth_headers(test_user_student, app)
    return access_headers


@pytest.fixture(scope="function")
def auth_headers_superadmin(app, test_user_superadmin):
    """Generate super admin authorization headers."""
    access_headers, _ = make_auth_headers(test_user_superadmin, app)
    return access_headers


@pytest.fixture(scope="function")
def test_institute(test_db, test_user_admin):
    """Create test institute."""
    return test_user_admin["institute"]


@pytest.fixture(scope="function")
def test_exam(test_db, test_user_teacher):
    """Create test exam with questions."""
    from bson import ObjectId
    
    exam_data = {
        "_id": ObjectId(),
        "title": "Test Exam",
        "description": "This is a test exam",
        "subject": "Mathematics",
        "topic": "Algebra",
        "institute_id": ObjectId(test_user_teacher["institute_id"]),
        "created_by_id": ObjectId(test_user_teacher["id"]),
        "exam_type": "institute",
        "status": "draft",
        "total_marks": 100,
        "passing_percentage": 40.0,
        "duration_minutes": 60,
        "result_mode": "instant",
        "access_mode": "open",
        "price": 0,
        "allowed_attempts": 1,
        "certificate_enabled": False,
        "schedule": {
            "start_at": datetime.utcnow() + timedelta(hours=1),
            "end_at": datetime.utcnow() + timedelta(days=1),
            "grace_minutes": 5,
        },
        "security": {
            "camera_required": False,
            "tab_switch_limit": 3,
            "fullscreen_required": False,
            "copy_paste_disabled": False,
            "shuffle_questions": False,
            "shuffle_options": False,
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    test_db.exams.insert_one(exam_data)
    
    question_data = {
        "_id": ObjectId(),
        "exam_id": exam_data["_id"],
        "created_by_id": ObjectId(test_user_teacher["id"]),
        "institute_id": ObjectId(test_user_teacher["institute_id"]),
        "question_text": "What is 2 + 2?",
        "question_type": "mcq",
        "options": [
            {"text": "3", "is_correct": False},
            {"text": "4", "is_correct": True},
            {"text": "5", "is_correct": False},
            {"text": "6", "is_correct": False},
        ],
        "correct_answer": "4",
        "marks": 10,
        "negative_marks": 0,
        "explanation": "Basic addition",
        "difficulty": "easy",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    test_db.questions.insert_one(question_data)
    
    exam_data["question_ids"] = [question_data["_id"]]
    test_db.exams.update_one(
        {"_id": exam_data["_id"]},
        {"$set": {"total_marks": question_data["marks"]}}
    )
    
    return {
        "id": str(exam_data["_id"]),
        "title": exam_data["title"],
        "description": exam_data["description"],
        "subject": exam_data["subject"],
        "status": exam_data["status"],
        "total_marks": exam_data["total_marks"],
        "duration_minutes": exam_data["duration_minutes"],
        "created_by_id": str(exam_data["created_by_id"]),
        "institute_id": str(exam_data["institute_id"]),
        "questions": [question_data],
    }


@pytest.fixture(scope="function")
def test_attempt(test_db, test_user_student, test_exam):
    """Create test exam attempt."""
    from bson import ObjectId
    
    attempt_data = {
        "_id": ObjectId(),
        "exam_id": ObjectId(test_exam["id"]),
        "user_id": ObjectId(test_user_student["id"]),
        "institute_id": ObjectId(test_user_student["institute_id"]),
        "status": "in_progress",
        "started_at": datetime.utcnow(),
        "answers": {},
        "score": 0,
        "total_marks": test_exam["total_marks"],
        "correct_answers": 0,
        "incorrect_answers": 0,
        "tab_switches": 0,
        "violations": [],
        "camera_enabled": False,
        "fullscreen_mode": True,
        "time_remaining_seconds": test_exam["duration_minutes"] * 60,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    test_db.exam_attempts.insert_one(attempt_data)
    
    return {
        "id": str(attempt_data["_id"]),
        "exam_id": str(attempt_data["exam_id"]),
        "user_id": str(attempt_data["user_id"]),
        "institute_id": str(attempt_data["institute_id"]),
        "status": attempt_data["status"],
        "started_at": attempt_data["started_at"],
        "answers": attempt_data["answers"],
        "score": attempt_data["score"],
        "tab_switches": attempt_data["tab_switches"],
    }


@pytest.fixture(scope="function")
def mock_razorpay():
    """Mock Razorpay client responses."""
    with patch('app.services.payment_service.RazorpayClient') as mock_client:
        mock_instance = MagicMock()
        
        mock_instance.order.create.return_value = {
            "id": "order_test123",
            "amount": 10000,
            "currency": "INR",
            "status": "created",
        }
        
        mock_instance.order.fetch.return_value = {
            "id": "order_test123",
            "amount": 10000,
            "currency": "INR",
            "status": "paid",
            "receipt": "test_receipt",
        }
        
        mock_instance.payment.fetch.return_value = {
            "id": "pay_test123",
            "amount": 10000,
            "currency": "INR",
            "status": "captured",
            "order_id": "order_test123",
        }
        
        mock_instance.utility.verify_signature.return_value = True
        
        mock_client.return_value = mock_instance
        
        yield mock_instance


@pytest.fixture(scope="function")
def mock_cloudinary():
    """Mock Cloudinary upload."""
    with patch('app.services.cloudinary_service.cloudinary.uploader.upload') as mock_upload:
        mock_upload.return_value = {
            "public_id": "test_public_id",
            "secure_url": "https://res.cloudinary.com/test/image/upload/test.jpg",
            "format": "jpg",
            "width": 800,
            "height": 600,
        }
        
        with patch('app.services.cloudinary_service.cloudinary.uploader.destroy') as mock_destroy:
            mock_destroy.return_value = {"result": "ok"}
            
            yield mock_upload


@pytest.fixture(scope="function")
def mock_email():
    """Mock email sending."""
    with patch('app.services.email_service.send_email') as mock_send:
        mock_send.return_value = True
        yield mock_send


@pytest.fixture(scope="function")
def mock_celery_task():
    """Mock Celery task execution."""
    with patch('app.tasks.email_tasks.send_otp_email.delay') as mock_task:
        mock_task.return_value = MagicMock(id="task_test123")
        yield mock_task
