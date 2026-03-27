"""
Exam management tests for ExamSaaS platform.
Tests cover exam creation, publishing, and scoring.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from bson import ObjectId


class TestExamCreate:
    """Test cases for exam creation."""
    
    def test_create_exam_as_teacher(self, client, test_db, auth_headers_teacher, test_user_teacher):
        """Test teacher can create exam."""
        response = client.post('/api/v1/exams',
            headers=auth_headers_teacher,
            json={
                "title": "New Test Exam",
                "description": "A comprehensive test exam",
                "subject": "Physics",
                "topic": "Mechanics",
                "duration_minutes": 90,
                "total_marks": 100,
                "passing_percentage": 40.0,
                "result_mode": "instant",
                "access_mode": "open",
                "price": 0,
                "allowed_attempts": 1,
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["title"] == "New Test Exam"
        assert data["data"]["status"] == "draft"
        
        exam = test_db.exams.find_one({"title": "New Test Exam"})
        assert exam is not None
        assert str(exam["created_by_id"]) == test_user_teacher["id"]
    
    def test_create_exam_as_student_forbidden(self, client, auth_headers_student):
        """Test student cannot create exam."""
        response = client.post('/api/v1/exams',
            headers=auth_headers_student,
            json={
                "title": "Student Exam",
                "description": "Should fail",
                "subject": "Math",
                "duration_minutes": 60,
            }
        )
        
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False
    
    def test_create_exam_missing_fields(self, client, auth_headers_teacher):
        """Test exam creation with missing required fields fails."""
        response = client.post('/api/v1/exams',
            headers=auth_headers_teacher,
            json={
                "title": "Incomplete Exam"
            }
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False
    
    def test_create_exam_invalid_duration(self, client, auth_headers_teacher):
        """Test exam creation with invalid duration fails."""
        response = client.post('/api/v1/exams',
            headers=auth_headers_teacher,
            json={
                "title": "Invalid Duration Exam",
                "subject": "Math",
                "duration_minutes": -5,
            }
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False
    
    def test_create_exam_with_schedule(self, client, test_db, auth_headers_teacher, test_user_teacher):
        """Test exam creation with schedule."""
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = datetime.utcnow() + timedelta(days=2)
        
        response = client.post('/api/v1/exams',
            headers=auth_headers_teacher,
            json={
                "title": "Scheduled Exam",
                "subject": "Chemistry",
                "duration_minutes": 60,
                "schedule": {
                    "start_at": start_time.isoformat(),
                    "end_at": end_time.isoformat(),
                    "grace_minutes": 10
                }
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["schedule"] is not None
    
    def test_create_exam_with_security(self, client, test_db, auth_headers_teacher, test_user_teacher):
        """Test exam creation with security settings."""
        response = client.post('/api/v1/exams',
            headers=auth_headers_teacher,
            json={
                "title": "Secure Exam",
                "subject": "Biology",
                "duration_minutes": 45,
                "security": {
                    "camera_required": True,
                    "tab_switch_limit": 2,
                    "fullscreen_required": True,
                    "copy_paste_disabled": True,
                }
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["security"]["camera_required"] is True
        assert data["data"]["security"]["tab_switch_limit"] == 2


class TestExamPublish:
    """Test cases for exam publishing."""
    
    def test_publish_exam(self, client, test_db, auth_headers_teacher, test_exam):
        """Test teacher can publish exam."""
        response = client.post(f'/api/v1/exams/{test_exam["id"]}/publish',
            headers=auth_headers_teacher
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["status"] == "published"
        
        exam = test_db.exams.find_one({"_id": ObjectId(test_exam["id"])})
        assert exam["status"] == "published"
    
    def test_publish_exam_without_questions(self, client, test_db, auth_headers_teacher, test_user_teacher):
        """Test publishing exam without questions fails."""
        exam_data = {
            "_id": ObjectId(),
            "title": "Empty Exam",
            "subject": "Math",
            "institute_id": ObjectId(test_user_teacher["institute_id"]),
            "created_by_id": ObjectId(test_user_teacher["id"]),
            "status": "draft",
            "duration_minutes": 60,
            "total_marks": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        test_db.exams.insert_one(exam_data)
        
        response = client.post(f'/api/v1/exams/{str(exam_data["_id"])}/publish',
            headers=auth_headers_teacher
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
    
    def test_publish_exam_unauthorized(self, client, test_exam, auth_headers_student):
        """Test non-owner cannot publish exam."""
        response = client.post(f'/api/v1/exams/{test_exam["id"]}/publish',
            headers=auth_headers_student
        )
        
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False
    
    def test_attempt_published_exam(self, client, test_db, test_exam, auth_headers_student, test_user_student):
        """Test student can attempt published exam."""
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
        
        response = client.post(f'/api/v1/exams/{test_exam["id"]}/attempt',
            headers=auth_headers_student
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert "attempt_id" in data["data"]
        
        attempt = test_db.exam_attempts.find_one({"_id": ObjectId(data["data"]["attempt_id"])})
        assert attempt is not None
        assert str(attempt["user_id"]) == test_user_student["id"]
    
    def test_attempt_unpublished_exam(self, client, test_exam, auth_headers_student):
        """Test cannot attempt unpublished exam."""
        response = client.post(f'/api/v1/exams/{test_exam["id"]}/attempt',
            headers=auth_headers_student
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False


class TestExamScoring:
    """Test cases for exam scoring."""
    
    def test_score_calculation(self, client, test_db, test_exam, auth_headers_student, test_user_student):
        """Test score is calculated correctly after submission."""
        test_db.exams.update_one(
            {"_id": ObjectId(test_exam["id"])},
            {"$set": {"status": "published"}}
        )
        
        attempt_data = {
            "_id": ObjectId(),
            "exam_id": ObjectId(test_exam["id"]),
            "user_id": ObjectId(test_user_student["id"]),
            "institute_id": ObjectId(test_user_student["institute_id"]),
            "status": "completed",
            "started_at": datetime.utcnow() - timedelta(minutes=30),
            "submitted_at": datetime.utcnow(),
            "answers": {
                str(test_exam["questions"][0]["_id"]): "4"
            },
            "score": 0,
            "total_marks": test_exam["total_marks"],
            "correct_answers": 0,
            "incorrect_answers": 0,
            "tab_switches": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        test_db.exam_attempts.insert_one(attempt_data)
        
        response = client.get(f'/api/v1/exams/{test_exam["id"]}/result/{str(attempt_data["_id"])}',
            headers=auth_headers_student
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["score"] == test_exam["total_marks"]
        assert data["data"]["correct_answers"] == 1
        assert data["data"]["passed"] is True
    
    def test_score_below_passing(self, client, test_db, test_exam, auth_headers_student, test_user_student):
        """Test score below passing percentage."""
        test_db.exams.update_one(
            {"_id": ObjectId(test_exam["id"])},
            {"$set": {"status": "published"}}
        )
        
        attempt_data = {
            "_id": ObjectId(),
            "exam_id": ObjectId(test_exam["id"]),
            "user_id": ObjectId(test_user_student["id"]),
            "institute_id": ObjectId(test_user_student["institute_id"]),
            "status": "completed",
            "started_at": datetime.utcnow() - timedelta(minutes=30),
            "submitted_at": datetime.utcnow(),
            "answers": {
                str(test_exam["questions"][0]["_id"]): "3"
            },
            "score": 0,
            "total_marks": test_exam["total_marks"],
            "correct_answers": 0,
            "incorrect_answers": 1,
            "tab_switches": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        test_db.exam_attempts.insert_one(attempt_data)
        
        response = client.get(f'/api/v1/exams/{test_exam["id"]}/result/{str(attempt_data["_id"])}',
            headers=auth_headers_student
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["score"] == 0
        assert data["data"]["passed"] is False


class TestExamList:
    """Test cases for exam listing."""
    
    def test_list_exams_as_teacher(self, client, test_db, auth_headers_teacher, test_exam):
        """Test teacher can list their exams."""
        response = client.get('/api/v1/exams',
            headers=auth_headers_teacher
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "exams" in data["data"]
        assert len(data["data"]["exams"]) >= 1
    
    def test_list_exams_as_student(self, client, test_db, auth_headers_student, test_exam):
        """Test student can list published exams."""
        test_db.exams.update_one(
            {"_id": ObjectId(test_exam["id"])},
            {"$set": {"status": "published"}}
        )
        
        response = client.get('/api/v1/exams',
            headers=auth_headers_student
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "exams" in data["data"]
    
    def test_list_exams_pagination(self, client, auth_headers_teacher):
        """Test exam listing with pagination."""
        response = client.get('/api/v1/exams?page=1&limit=10',
            headers=auth_headers_teacher
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "pagination" in data["data"]


class TestExamUpdate:
    """Test cases for exam updates."""
    
    def test_update_exam_as_owner(self, client, test_db, auth_headers_teacher, test_exam):
        """Test owner can update exam."""
        response = client.put(f'/api/v1/exams/{test_exam["id"]}',
            headers=auth_headers_teacher,
            json={
                "title": "Updated Title",
                "description": "Updated description"
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["title"] == "Updated Title"
        
        exam = test_db.exams.find_one({"_id": ObjectId(test_exam["id"])})
        assert exam["title"] == "Updated Title"
    
    def test_update_exam_status_restriction(self, client, test_db, auth_headers_teacher, test_exam):
        """Test cannot update published exam."""
        test_db.exams.update_one(
            {"_id": ObjectId(test_exam["id"])},
            {"$set": {"status": "published"}}
        )
        
        response = client.put(f'/api/v1/exams/{test_exam["id"]}',
            headers=auth_headers_teacher,
            json={
                "title": "Should Not Update"
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
    
    def test_delete_exam(self, client, test_db, auth_headers_teacher, test_exam):
        """Test owner can delete exam."""
        response = client.delete(f'/api/v1/exams/{test_exam["id"]}',
            headers=auth_headers_teacher
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        
        exam = test_db.exams.find_one({"_id": ObjectId(test_exam["id"])})
        assert exam is None


class TestExamQuestions:
    """Test cases for exam questions."""
    
    def test_add_question_to_exam(self, client, test_db, auth_headers_teacher, test_exam):
        """Test adding question to exam."""
        response = client.post(f'/api/v1/exams/{test_exam["id"]}/questions',
            headers=auth_headers_teacher,
            json={
                "question_text": "What is 3 + 3?",
                "question_type": "mcq",
                "options": [
                    {"text": "5", "is_correct": False},
                    {"text": "6", "is_correct": True},
                    {"text": "7", "is_correct": False},
                ],
                "marks": 5,
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["question_text"] == "What is 3 + 3?"
        
        question = test_db.questions.find_one({"exam_id": ObjectId(test_exam["id"])})
        assert question is not None
