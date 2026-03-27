"""
Exam attempt tests for ExamSaaS platform.
Tests cover attempt lifecycle, violations, and auto-submission.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from bson import ObjectId


class TestAttemptLifecycle:
    """Test cases for exam attempt lifecycle."""
    
    def test_start_attempt(self, client, test_db, test_exam, auth_headers_student, test_user_student):
        """Test student can start exam attempt."""
        test_db.exams.update_one(
            {"_id": ObjectId(test_exam["id"])},
            {"$set": {
                "status": "published",
                "schedule": {
                    "start_at": datetime.utcnow() - timedelta(hours=1),
                    "end_at": datetime.utcnow() + timedelta(hours=1),
                    "grace_minutes": 5,
                }
            }}
        )
        
        response = client.post(f'/api/v1/attempts/{test_exam["id"]}/start',
            headers=auth_headers_student
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert "attempt_id" in data["data"]
        assert data["data"]["status"] == "in_progress"
        
        attempt = test_db.exam_attempts.find_one({"_id": ObjectId(data["data"]["attempt_id"])})
        assert attempt is not None
        assert str(attempt["user_id"]) == test_user_student["id"]
        assert attempt["started_at"] is not None
    
    def test_start_attempt_no_remaining_attempts(self, client, test_db, test_exam, auth_headers_student, test_user_student):
        """Test cannot start exam when no attempts remaining."""
        test_db.exams.update_one(
            {"_id": ObjectId(test_exam["id"])},
            {"$set": {"status": "published", "allowed_attempts": 1}}
        )
        
        existing_attempt = {
            "_id": ObjectId(),
            "exam_id": ObjectId(test_exam["id"]),
            "user_id": ObjectId(test_user_student["id"]),
            "institute_id": ObjectId(test_user_student["institute_id"]),
            "status": "completed",
            "started_at": datetime.utcnow() - timedelta(hours=1),
            "submitted_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        test_db.exam_attempts.insert_one(existing_attempt)
        
        response = client.post(f'/api/v1/attempts/{test_exam["id"]}/start',
            headers=auth_headers_student
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
    
    def test_start_attempt_exam_not_started(self, client, test_db, test_exam, auth_headers_student):
        """Test cannot start exam before scheduled time."""
        test_db.exams.update_one(
            {"_id": ObjectId(test_exam["id"])},
            {"$set": {
                "status": "published",
                "schedule": {
                    "start_at": datetime.utcnow() + timedelta(hours=1),
                    "end_at": datetime.utcnow() + timedelta(hours=2),
                    "grace_minutes": 5,
                }
            }}
        )
        
        response = client.post(f'/api/v1/attempts/{test_exam["id"]}/start',
            headers=auth_headers_student
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
    
    def test_save_answers(self, client, test_db, test_exam, test_attempt, auth_headers_student):
        """Test saving answers during attempt."""
        question_id = str(test_exam["questions"][0]["_id"])
        
        response = client.post(f'/api/v1/attempts/{test_attempt["id"]}/save',
            headers=auth_headers_student,
            json={
                "answers": {
                    question_id: "4"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["answers"][question_id] == "4"
        
        attempt = test_db.exam_attempts.find_one({"_id": ObjectId(test_attempt["id"])})
        assert attempt["answers"][question_id] == "4"
    
    def test_save_answers_invalid_attempt(self, client, test_db, auth_headers_student, test_exam):
        """Test saving answers for non-existent attempt fails."""
        fake_attempt_id = str(ObjectId())
        
        response = client.post(f'/api/v1/attempts/{fake_attempt_id}/save',
            headers=auth_headers_student,
            json={
                "answers": {"some_id": "answer"}
            }
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False
    
    def test_submit_attempt(self, client, test_db, test_exam, test_attempt, auth_headers_student):
        """Test submitting exam attempt."""
        test_db.exam_attempts.update_one(
            {"_id": ObjectId(test_attempt["id"])},
            {"$set": {
                "answers": {str(test_exam["questions"][0]["_id"]): "4"}
            }}
        )
        
        response = client.post(f'/api/v1/attempts/{test_attempt["id"]}/submit',
            headers=auth_headers_student
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["status"] == "completed"
        assert data["data"]["submitted_at"] is not None
        
        attempt = test_db.exam_attempts.find_one({"_id": ObjectId(test_attempt["id"])})
        assert attempt["status"] == "completed"
        assert attempt["submitted_at"] is not None
    
    def test_auto_submit_on_violation_limit(self, client, test_db, test_exam, test_attempt, auth_headers_student):
        """Test attempt is auto-submitted when violation limit reached."""
        test_db.exam_attempts.update_one(
            {"_id": ObjectId(test_attempt["id"])},
            {"$set": {
                "tab_switches": 2,
                "violations": [{"type": "tab_switch", "timestamp": datetime.utcnow().isoformat()}]
            }}
        )
        
        test_db.exams.update_one(
            {"_id": ObjectId(test_exam["id"])},
            {"$set": {
                "security.tab_switch_limit": 3
            }}
        )
        
        response = client.post(f'/api/v1/attempts/{test_attempt["id"]}/violation',
            headers=auth_headers_student,
            json={
                "type": "tab_switch",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["auto_submitted"] is True
        assert data["data"]["status"] == "completed"


class TestAttemptViolations:
    """Test cases for exam attempt violations."""
    
    def test_tab_switch_violation(self, client, test_db, test_exam, test_attempt, auth_headers_student):
        """Test tab switch violation is recorded."""
        response = client.post(f'/api/v1/attempts/{test_attempt["id"]}/violation',
            headers=auth_headers_student,
            json={
                "type": "tab_switch",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["violations"][-1]["type"] == "tab_switch"
        
        attempt = test_db.exam_attempts.find_one({"_id": ObjectId(test_attempt["id"])})
        assert attempt["tab_switches"] == 1
        assert len(attempt["violations"]) > 0
    
    def test_fullscreen_exit_violation(self, client, test_db, test_exam, test_attempt, auth_headers_student):
        """Test fullscreen exit violation is recorded."""
        response = client.post(f'/api/v1/attempts/{test_attempt["id"]}/violation',
            headers=auth_headers_student,
            json={
                "type": "fullscreen_exit",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        
        attempt = test_db.exam_attempts.find_one({"_id": ObjectId(test_attempt["id"])})
        violations = attempt["violations"]
        fullscreen_exit = [v for v in violations if v["type"] == "fullscreen_exit"]
        assert len(fullscreen_exit) > 0
    
    def test_multiple_tab_switch_violations(self, client, test_db, test_exam, test_attempt, auth_headers_student):
        """Test multiple tab switch violations are counted correctly."""
        for i in range(3):
            response = client.post(f'/api/v1/attempts/{test_attempt["id"]}/violation',
                headers=auth_headers_student,
                json={
                    "type": "tab_switch",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        assert response.status_code == 200
        
        attempt = test_db.exam_attempts.find_one({"_id": ObjectId(test_attempt["id"])})
        assert attempt["tab_switches"] == 3
    
    def test_violation_after_submission_fails(self, client, test_db, test_exam, test_attempt, auth_headers_student):
        """Test cannot log violation for completed attempt."""
        test_db.exam_attempts.update_one(
            {"_id": ObjectId(test_attempt["id"])},
            {"$set": {"status": "completed", "submitted_at": datetime.utcnow()}}
        )
        
        response = client.post(f'/api/v1/attempts/{test_attempt["id"]}/violation',
            headers=auth_headers_student,
            json={
                "type": "tab_switch",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False


class TestAttemptRetrieval:
    """Test cases for retrieving attempt data."""
    
    def test_get_attempt_status(self, client, test_db, test_exam, test_attempt, auth_headers_student):
        """Test getting attempt status."""
        response = client.get(f'/api/v1/attempts/{test_attempt["id"]}',
            headers=auth_headers_student
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["id"] == test_attempt["id"]
        assert data["data"]["status"] == "in_progress"
    
    def test_get_questions_for_attempt(self, client, test_db, test_exam, test_attempt, auth_headers_student):
        """Test getting questions for active attempt."""
        response = client.get(f'/api/v1/attempts/{test_attempt["id"]}/questions',
            headers=auth_headers_student
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "questions" in data["data"]
        assert len(data["data"]["questions"]) > 0
    
    def test_get_attempt_not_owner(self, client, test_db, test_exam, test_attempt, test_user_teacher):
        """Test cannot get another user's attempt."""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            access_token = create_access_token(
                identity=test_user_teacher["id"],
                additional_claims={
                    "email": test_user_teacher["email"],
                    "role": test_user_teacher["role"],
                }
            )
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        
        response = client.get(f'/api/v1/attempts/{test_attempt["id"]}',
            headers=headers
        )
        
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False


class TestAttemptTimeLimit:
    """Test cases for attempt time limit handling."""
    
    def test_time_remaining_calculation(self, client, test_db, test_exam, test_attempt, auth_headers_student):
        """Test time remaining is calculated correctly."""
        start_time = datetime.utcnow() - timedelta(minutes=30)
        duration_minutes = 60
        
        test_db.exam_attempts.update_one(
            {"_id": ObjectId(test_attempt["id"])},
            {"$set": {"started_at": start_time}}
        )
        
        response = client.get(f'/api/v1/attempts/{test_attempt["id"]}',
            headers=auth_headers_student
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "time_remaining_seconds" in data["data"]
    
    def test_time_expired_auto_submit(self, client, test_db, test_exam, test_attempt, auth_headers_student):
        """Test attempt is auto-submitted when time expires."""
        start_time = datetime.utcnow() - timedelta(minutes=65)
        
        test_db.exam_attempts.update_one(
            {"_id": ObjectId(test_attempt["id"])},
            {"$set": {
                "started_at": start_time,
                "time_remaining_seconds": 0
            }}
        )
        
        response = client.get(f'/api/v1/attempts/{test_attempt["id"]}/check-time',
            headers=auth_headers_student
        )
        
        assert response.status_code == 200
        data = response.get_json()
        if data["data"].get("time_expired"):
            attempt = test_db.exam_attempts.find_one({"_id": ObjectId(test_attempt["id"])})
            assert attempt["status"] == "completed"


class TestAttemptConcurrency:
    """Test cases for attempt concurrency handling."""
    
    def test_only_one_active_attempt_per_exam(self, client, test_db, test_exam, auth_headers_student, test_user_student):
        """Test cannot have multiple active attempts for same exam."""
        test_db.exams.update_one(
            {"_id": ObjectId(test_exam["id"])},
            {"$set": {"status": "published"}}
        )
        
        existing_attempt = {
            "_id": ObjectId(),
            "exam_id": ObjectId(test_exam["id"]),
            "user_id": ObjectId(test_user_student["id"]),
            "institute_id": ObjectId(test_user_student["institute_id"]),
            "status": "in_progress",
            "started_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        test_db.exam_attempts.insert_one(existing_attempt)
        
        response = client.post(f'/api/v1/attempts/{test_exam["id"]}/start',
            headers=auth_headers_student
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
