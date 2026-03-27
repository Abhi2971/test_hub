"""
Payment tests for ExamSaaS platform.
Tests cover Razorpay order creation, webhook handling, and idempotency.
"""
import pytest
import json
import hmac
import hashlib
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from bson import ObjectId


class TestRazorpayOrder:
    """Test cases for Razorpay order creation."""
    
    def test_create_order(self, client, test_db, test_exam, auth_headers_student, test_user_student, mock_razorpay):
        """Test creating payment order for exam."""
        test_db.exams.update_one(
            {"_id": ObjectId(test_exam["id"])},
            {"$set": {"price": 10000}}
        )
        
        response = client.post('/api/v1/payments/create-order',
            headers=auth_headers_student,
            json={
                "exam_id": test_exam["id"],
                "amount": 10000,
                "currency": "INR",
                "purpose": "exam_purchase"
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert "order_id" in data["data"]
        assert data["data"]["razorpay_order_id"] == "order_test123"
        
        payment = test_db.payments.find_one({"razorpay_order_id": "order_test123"})
        assert payment is not None
        assert payment["user_id"] == ObjectId(test_user_student["id"])
    
    def test_create_order_insufficient_balance(self, client, test_db, test_exam, auth_headers_student, test_user_student):
        """Test creating order fails with insufficient wallet balance."""
        test_db.wallets.update_one(
            {"_id": ObjectId(test_user_student["wallet_id"])},
            {"$set": {"balance": 100}}
        )
        
        response = client.post('/api/v1/payments/create-order',
            headers=auth_headers_student,
            json={
                "exam_id": test_exam["id"],
                "amount": 10000,
                "currency": "INR",
                "purpose": "wallet_topup"
            }
        )
        
        assert response.status_code == 402
        data = response.get_json()
        assert data["success"] is False
    
    def test_create_order_wallet_topup(self, client, test_db, auth_headers_student, test_user_student, mock_razorpay):
        """Test creating order for wallet top-up."""
        response = client.post('/api/v1/payments/create-order',
            headers=auth_headers_student,
            json={
                "amount": 50000,
                "currency": "INR",
                "purpose": "wallet_topup"
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert "order_id" in data["data"]
        
        payment = test_db.payments.find_one({"razorpay_order_id": "order_test123"})
        assert payment is not None
        assert payment["purpose"] == "wallet_topup"
        assert payment["amount"] == 50000
    
    def test_create_order_invalid_amount(self, client, auth_headers_student):
        """Test creating order with invalid amount fails."""
        response = client.post('/api/v1/payments/create-order',
            headers=auth_headers_student,
            json={
                "amount": -100,
                "currency": "INR",
                "purpose": "wallet_topup"
            }
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False
    
    def test_create_order_missing_fields(self, client, auth_headers_student):
        """Test creating order with missing fields fails."""
        response = client.post('/api/v1/payments/create-order',
            headers=auth_headers_student,
            json={
                "amount": 10000
            }
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False


class TestRazorpayWebhook:
    """Test cases for Razorpay webhook handling."""
    
    def test_webhook_signature_verification(self, client, test_db, mock_razorpay):
        """Test webhook signature verification."""
        payload = json.dumps({
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_test123",
                        "order_id": "order_test123",
                        "amount": 10000,
                        "currency": "INR",
                        "status": "captured"
                    }
                }
            }
        })
        
        webhook_secret = "test_webhook_secret"
        signature = hmac.new(
            webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        with patch('app.services.payment_service.RAZORPAY_WEBHOOK_SECRET', webhook_secret):
            response = client.post('/api/v1/payments/webhook',
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Razorpay-Signature": signature
                }
            )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
    
    def test_webhook_payment_captured(self, client, test_db, mock_razorpay):
        """Test payment captured webhook updates order status."""
        payment_data = {
            "_id": ObjectId(),
            "razorpay_order_id": "order_webhook_test",
            "user_id": ObjectId(),
            "amount": 10000,
            "status": "pending",
            "purpose": "wallet_topup",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        test_db.payments.insert_one(payment_data)
        
        payload = json.dumps({
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_webhook123",
                        "order_id": "order_webhook_test",
                        "amount": 10000,
                        "currency": "INR",
                        "status": "captured"
                    }
                }
            }
        })
        
        webhook_secret = "test_webhook_secret"
        signature = hmac.new(
            webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        with patch('app.services.payment_service.RAZORPAY_WEBHOOK_SECRET', webhook_secret):
            response = client.post('/api/v1/payments/webhook',
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Razorpay-Signature": signature
                }
            )
        
        assert response.status_code == 200
        
        payment = test_db.payments.find_one({"razorpay_order_id": "order_webhook_test"})
        assert payment["status"] == "captured"
    
    def test_webhook_invalid_signature(self, client):
        """Test webhook with invalid signature is rejected."""
        payload = json.dumps({
            "event": "payment.captured",
            "payload": {}
        })
        
        response = client.post('/api/v1/payments/webhook',
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-Razorpay-Signature": "invalid_signature_here"
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
    
    def test_webhook_payment_failed(self, client, test_db, mock_razorpay):
        """Test payment failed webhook updates order status."""
        payment_data = {
            "_id": ObjectId(),
            "razorpay_order_id": "order_failed_test",
            "user_id": ObjectId(),
            "amount": 10000,
            "status": "pending",
            "purpose": "wallet_topup",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        test_db.payments.insert_one(payment_data)
        
        payload = json.dumps({
            "event": "payment.failed",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_failed123",
                        "order_id": "order_failed_test",
                        "amount": 10000,
                        "currency": "INR",
                        "status": "failed"
                    }
                }
            }
        })
        
        webhook_secret = "test_webhook_secret"
        signature = hmac.new(
            webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        with patch('app.services.payment_service.RAZORPAY_WEBHOOK_SECRET', webhook_secret):
            response = client.post('/api/v1/payments/webhook',
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Razorpay-Signature": signature
                }
            )
        
        assert response.status_code == 200
        
        payment = test_db.payments.find_one({"razorpay_order_id": "order_failed_test"})
        assert payment["status"] == "failed"


class TestIdempotency:
    """Test cases for payment idempotency."""
    
    def test_payment_idempotency(self, client, test_db, auth_headers_student, test_user_student, mock_razorpay):
        """Test duplicate order creation with same idempotency key returns same order."""
        idempotency_key = "test_idempotency_key_123"
        
        response1 = client.post('/api/v1/payments/create-order',
            headers=auth_headers_student,
            json={
                "amount": 10000,
                "currency": "INR",
                "purpose": "wallet_topup",
                "idempotency_key": idempotency_key
            }
        )
        
        assert response1.status_code == 201
        data1 = response1.get_json()
        order_id_1 = data1["data"]["order_id"]
        
        response2 = client.post('/api/v1/payments/create-order',
            headers=auth_headers_student,
            json={
                "amount": 10000,
                "currency": "INR",
                "purpose": "wallet_topup",
                "idempotency_key": idempotency_key
            }
        )
        
        assert response2.status_code == 200
        data2 = response2.get_json()
        order_id_2 = data2["data"]["order_id"]
        
        assert order_id_1 == order_id_2
        
        payments_count = test_db.payments.count_documents({
            "user_id": ObjectId(test_user_student["id"]),
            "purpose": "wallet_topup"
        })
        assert payments_count == 1
    
    def test_different_idempotency_keys_create_different_orders(self, client, test_db, auth_headers_student, test_user_student, mock_razorpay):
        """Test different idempotency keys create different orders."""
        response1 = client.post('/api/v1/payments/create-order',
            headers=auth_headers_student,
            json={
                "amount": 10000,
                "currency": "INR",
                "purpose": "wallet_topup",
                "idempotency_key": "key_1"
            }
        )
        
        assert response1.status_code == 201
        
        response2 = client.post('/api/v1/payments/create-order',
            headers=auth_headers_student,
            json={
                "amount": 10000,
                "currency": "INR",
                "purpose": "wallet_topup",
                "idempotency_key": "key_2"
            }
        )
        
        assert response2.status_code == 201
        
        payments_count = test_db.payments.count_documents({
            "user_id": ObjectId(test_user_student["id"]),
            "purpose": "wallet_topup"
        })
        assert payments_count == 2


class TestPaymentVerification:
    """Test cases for payment verification."""
    
    def test_verify_payment_success(self, client, test_db, auth_headers_student, test_user_student, mock_razorpay):
        """Test successful payment verification."""
        payment_data = {
            "_id": ObjectId(),
            "razorpay_order_id": "order_verify_test",
            "user_id": ObjectId(test_user_student["id"]),
            "amount": 10000,
            "status": "pending",
            "purpose": "wallet_topup",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        test_db.payments.insert_one(payment_data)
        
        response = client.post('/api/v1/payments/verify',
            headers=auth_headers_student,
            json={
                "razorpay_order_id": "order_verify_test",
                "razorpay_payment_id": "pay_verify123",
                "razorpay_signature": "valid_signature"
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        
        payment = test_db.payments.find_one({"razorpay_order_id": "order_verify_test"})
        assert payment["status"] == "captured"
    
    def test_verify_payment_invalid_signature(self, client, test_db, auth_headers_student, test_user_student):
        """Test payment verification with invalid signature fails."""
        payment_data = {
            "_id": ObjectId(),
            "razorpay_order_id": "order_invalid_sig",
            "user_id": ObjectId(test_user_student["id"]),
            "amount": 10000,
            "status": "pending",
            "purpose": "wallet_topup",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        test_db.payments.insert_one(payment_data)
        
        response = client.post('/api/v1/payments/verify',
            headers=auth_headers_student,
            json={
                "razorpay_order_id": "order_invalid_sig",
                "razorpay_payment_id": "pay_invalid123",
                "razorpay_signature": "invalid_signature"
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False


class TestPaymentHistory:
    """Test cases for payment history."""
    
    def test_get_payment_history(self, client, test_db, auth_headers_student, test_user_student):
        """Test getting user payment history."""
        for i in range(3):
            payment_data = {
                "_id": ObjectId(),
                "razorpay_order_id": f"order_history_{i}",
                "user_id": ObjectId(test_user_student["id"]),
                "amount": 10000 * (i + 1),
                "status": "captured",
                "purpose": "wallet_topup",
                "created_at": datetime.utcnow() - timedelta(days=i),
                "updated_at": datetime.utcnow(),
            }
            test_db.payments.insert_one(payment_data)
        
        response = client.get('/api/v1/payments/history',
            headers=auth_headers_student
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "payments" in data["data"]
        assert len(data["data"]["payments"]) == 3
    
    def test_get_payment_by_id(self, client, test_db, auth_headers_student, test_user_student):
        """Test getting specific payment by ID."""
        payment_data = {
            "_id": ObjectId(),
            "razorpay_order_id": "order_specific",
            "user_id": ObjectId(test_user_student["id"]),
            "amount": 15000,
            "status": "captured",
            "purpose": "wallet_topup",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        test_db.payments.insert_one(payment_data)
        
        response = client.get(f'/api/v1/payments/{str(payment_data["_id"])}',
            headers=auth_headers_student
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["razorpay_order_id"] == "order_specific"
