"""
Wallet tests for ExamSaaS platform.
Tests cover credit, debit, concurrency, and atomicity.
"""
import pytest
import threading
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from bson import ObjectId


class TestWalletCredit:
    """Test cases for wallet credit operations."""
    
    def test_credit_success(self, client, test_db, auth_headers_student, test_user_student):
        """Test successful wallet credit."""
        initial_balance = test_user_student["wallet"]["balance"]
        
        response = client.post('/api/v1/wallet/credit',
            headers=auth_headers_student,
            json={
                "amount": 10000,
                "purpose": "top_up",
                "reference_id": "ref_credit_001"
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["balance"] == initial_balance + 10000
        
        wallet = test_db.wallets.find_one({"_id": ObjectId(test_user_student["wallet_id"])})
        assert wallet["balance"] == initial_balance + 10000
        assert wallet["total_credited"] == initial_balance + 10000
        
        transaction = test_db.wallet_transactions.find_one({"reference_id": "ref_credit_001"})
        assert transaction is not None
        assert transaction["type"] == "credit"
        assert transaction["amount"] == 10000
    
    def test_credit_negative_amount_rejected(self, client, test_db, auth_headers_student, test_user_student):
        """Test credit with negative amount is rejected."""
        response = client.post('/api/v1/wallet/credit',
            headers=auth_headers_student,
            json={
                "amount": -5000,
                "purpose": "top_up"
            }
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False
        
        wallet = test_db.wallets.find_one({"_id": ObjectId(test_user_student["wallet_id"])})
        assert wallet["balance"] == test_user_student["wallet"]["balance"]
    
    def test_credit_zero_amount_rejected(self, client, test_db, auth_headers_student, test_user_student):
        """Test credit with zero amount is rejected."""
        response = client.post('/api/v1/wallet/credit',
            headers=auth_headers_student,
            json={
                "amount": 0,
                "purpose": "top_up"
            }
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False
    
    def test_credit_missing_fields(self, client, auth_headers_student):
        """Test credit with missing fields fails."""
        response = client.post('/api/v1/wallet/credit',
            headers=auth_headers_student,
            json={
                "amount": 10000
            }
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False


class TestWalletDebit:
    """Test cases for wallet debit operations."""
    
    def test_debit_success(self, client, test_db, auth_headers_student, test_user_student):
        """Test successful wallet debit."""
        initial_balance = test_user_student["wallet"]["balance"]
        
        response = client.post('/api/v1/wallet/debit',
            headers=auth_headers_student,
            json={
                "amount": 5000,
                "purpose": "exam_purchase",
                "reference_id": "ref_debit_001"
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["balance"] == initial_balance - 5000
        
        wallet = test_db.wallets.find_one({"_id": ObjectId(test_user_student["wallet_id"])})
        assert wallet["balance"] == initial_balance - 5000
        assert wallet["total_debited"] == 5000
        
        transaction = test_db.wallet_transactions.find_one({"reference_id": "ref_debit_001"})
        assert transaction is not None
        assert transaction["type"] == "debit"
        assert transaction["amount"] == 5000
    
    def test_debit_insufficient_balance(self, client, test_db, auth_headers_student, test_user_student):
        """Test debit with insufficient balance fails."""
        response = client.post('/api/v1/wallet/debit',
            headers=auth_headers_student,
            json={
                "amount": test_user_student["wallet"]["balance"] + 1000,
                "purpose": "exam_purchase"
            }
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False
        assert "insufficient" in data["message"].lower()
        
        wallet = test_db.wallets.find_one({"_id": ObjectId(test_user_student["wallet_id"])})
        assert wallet["balance"] == test_user_student["wallet"]["balance"]
    
    def test_debit_below_zero_rejected(self, client, test_db, auth_headers_student, test_user_student):
        """Test debit that would result in negative balance is rejected."""
        current_balance = test_user_student["wallet"]["balance"]
        debit_amount = current_balance + 1
        
        response = client.post('/api/v1/wallet/debit',
            headers=auth_headers_student,
            json={
                "amount": debit_amount,
                "purpose": "exam_purchase"
            }
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False
        
        wallet = test_db.wallets.find_one({"_id": ObjectId(test_user_student["wallet_id"])})
        assert wallet["balance"] == current_balance
        assert wallet["balance"] >= 0
    
    def test_debit_exact_balance(self, client, test_db, auth_headers_student, test_user_student):
        """Test debit of exact balance amount succeeds."""
        test_db.wallets.update_one(
            {"_id": ObjectId(test_user_student["wallet_id"])},
            {"$set": {"balance": 10000}}
        )
        
        response = client.post('/api/v1/wallet/debit',
            headers=auth_headers_student,
            json={
                "amount": 10000,
                "purpose": "exam_purchase"
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["balance"] == 0
    
    def test_concurrent_debit_only_one_succeeds(self, client, test_db, auth_headers_student, test_user_student):
        """Test that concurrent debits don't cause race conditions."""
        test_db.wallets.update_one(
            {"_id": ObjectId(test_user_student["wallet_id"])},
            {"$set": {"balance": 10000, "version": 0}}
        )
        
        results = {"success": 0, "failure": 0}
        results_lock = threading.Lock()
        
        def attempt_debit():
            nonlocal results
            with client.application.test_request_context():
                response = client.post('/api/v1/wallet/debit',
                    headers=auth_headers_student,
                    json={
                        "amount": 10000,
                        "purpose": "exam_purchase",
                        "reference_id": f"ref_concurrent_{threading.current_thread().ident}"
                    }
                )
                with results_lock:
                    if response.status_code == 200:
                        results["success"] += 1
                    else:
                        results["failure"] += 1
        
        threads = []
        for _ in range(2):
            t = threading.Thread(target=attempt_debit)
            threads.append(t)
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        assert results["success"] == 1
        assert results["failure"] == 1
        
        wallet = test_db.wallets.find_one({"_id": ObjectId(test_user_student["wallet_id"])})
        assert wallet["balance"] >= 0
        assert wallet["balance"] <= 10000
    
    def test_credit_debit_atomic(self, client, test_db, auth_headers_student, test_user_student):
        """Test that credit and debit operations are atomic."""
        initial_balance = test_user_student["wallet"]["balance"]
        
        client.post('/api/v1/wallet/credit',
            headers=auth_headers_student,
            json={
                "amount": 5000,
                "purpose": "top_up",
                "reference_id": "ref_atomic_credit"
            }
        )
        
        client.post('/api/v1/wallet/debit',
            headers=auth_headers_student,
            json={
                "amount": 3000,
                "purpose": "exam_purchase",
                "reference_id": "ref_atomic_debit"
            }
        )
        
        wallet = test_db.wallets.find_one({"_id": ObjectId(test_user_student["wallet_id"])})
        expected_balance = initial_balance + 5000 - 3000
        assert wallet["balance"] == expected_balance
        assert wallet["total_credited"] == initial_balance + 5000
        assert wallet["total_debited"] == 3000
        
        credit_txn = test_db.wallet_transactions.find_one({"reference_id": "ref_atomic_credit"})
        debit_txn = test_db.wallet_transactions.find_one({"reference_id": "ref_atomic_debit"})
        
        assert credit_txn["balance_after"] == initial_balance + 5000
        assert debit_txn["balance_after"] == expected_balance


class TestWalletBalance:
    """Test cases for wallet balance operations."""
    
    def test_get_balance(self, client, test_db, auth_headers_student, test_user_student):
        """Test getting wallet balance."""
        response = client.get('/api/v1/wallet/balance',
            headers=auth_headers_student
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["balance"] == test_user_student["wallet"]["balance"]
        assert data["data"]["currency"] == "INR"
    
    def test_get_wallet_history(self, client, test_db, auth_headers_student, test_user_student):
        """Test getting wallet transaction history."""
        for i in range(5):
            if i % 2 == 0:
                test_db.wallet_transactions.insert_one({
                    "_id": ObjectId(),
                    "wallet_id": ObjectId(test_user_student["wallet_id"]),
                    "user_id": ObjectId(test_user_student["id"]),
                    "type": "credit",
                    "amount": 1000 * (i + 1),
                    "balance_after": test_user_student["wallet"]["balance"] + 1000 * (i + 1),
                    "purpose": "top_up",
                    "source": "razorpay",
                    "reference_id": f"ref_history_{i}",
                    "created_at": datetime.utcnow() - timedelta(hours=i),
                    "updated_at": datetime.utcnow(),
                })
            else:
                test_db.wallet_transactions.insert_one({
                    "_id": ObjectId(),
                    "wallet_id": ObjectId(test_user_student["wallet_id"]),
                    "user_id": ObjectId(test_user_student["id"]),
                    "type": "debit",
                    "amount": 500 * i,
                    "balance_after": test_user_student["wallet"]["balance"] + 1000 * i,
                    "purpose": "exam_purchase",
                    "source": "system",
                    "reference_id": f"ref_history_{i}",
                    "created_at": datetime.utcnow() - timedelta(hours=i),
                    "updated_at": datetime.utcnow(),
                })
        
        response = client.get('/api/v1/wallet/history',
            headers=auth_headers_student
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "transactions" in data["data"]
        assert len(data["data"]["transactions"]) == 5


class TestWalletValidation:
    """Test cases for wallet validation."""
    
    def test_negative_amount_validation(self, client, auth_headers_student):
        """Test negative amounts are validated."""
        response = client.post('/api/v1/wallet/debit',
            headers=auth_headers_student,
            json={
                "amount": -100,
                "purpose": "test"
            }
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False
    
    def test_zero_amount_validation(self, client, auth_headers_student):
        """Test zero amounts are validated."""
        response = client.post('/api/v1/wallet/credit',
            headers=auth_headers_student,
            json={
                "amount": 0,
                "purpose": "test"
            }
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False
    
    def test_exceeds_maximum_amount(self, client, auth_headers_student):
        """Test amounts exceeding maximum are validated."""
        response = client.post('/api/v1/wallet/credit',
            headers=auth_headers_student,
            json={
                "amount": 1000000001,
                "purpose": "top_up"
            }
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False


class TestWalletEdgeCases:
    """Test cases for wallet edge cases."""
    
    def test_debit_creates_transaction_on_success(self, client, test_db, auth_headers_student, test_user_student):
        """Test that successful debit creates transaction record."""
        initial_txn_count = test_db.wallet_transactions.count_documents({
            "user_id": ObjectId(test_user_student["id"])
        })
        
        client.post('/api/v1/wallet/debit',
            headers=auth_headers_student,
            json={
                "amount": 1000,
                "purpose": "exam_purchase",
                "reference_id": "ref_debit_txn"
            }
        )
        
        new_txn_count = test_db.wallet_transactions.count_documents({
            "user_id": ObjectId(test_user_student["id"])
        })
        
        assert new_txn_count == initial_txn_count + 1
        
        transaction = test_db.wallet_transactions.find_one({"reference_id": "ref_debit_txn"})
        assert transaction is not None
        assert transaction["type"] == "debit"
    
    def test_concurrent_credits_are_consistent(self, client, test_db, auth_headers_student, test_user_student):
        """Test concurrent credits maintain consistency."""
        test_db.wallets.update_one(
            {"_id": ObjectId(test_user_student["wallet_id"])},
            {"$set": {"balance": 0, "version": 0}}
        )
        
        results = {"success": 0}
        
        def attempt_credit():
            nonlocal results
            response = client.post('/api/v1/wallet/credit',
                headers=auth_headers_student,
                json={
                    "amount": 1000,
                    "purpose": "top_up",
                    "reference_id": f"ref_concurrent_credit_{threading.current_thread().ident}"
                }
            )
            if response.status_code == 200:
                results["success"] += 1
        
        threads = []
        for _ in range(5):
            t = threading.Thread(target=attempt_credit)
            threads.append(t)
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        assert results["success"] == 5
        
        wallet = test_db.wallets.find_one({"_id": ObjectId(test_user_student["wallet_id"])})
        assert wallet["balance"] == 5000
        assert wallet["total_credited"] == 5000
    
    def test_wallet_version_increments(self, client, test_db, auth_headers_student, test_user_student):
        """Test wallet version increments on each operation."""
        initial_version = test_user_student["wallet"]["version"]
        
        client.post('/api/v1/wallet/credit',
            headers=auth_headers_student,
            json={
                "amount": 1000,
                "purpose": "top_up"
            }
        )
        
        wallet = test_db.wallets.find_one({"_id": ObjectId(test_user_student["wallet_id"])})
        assert wallet["version"] == initial_version + 1
        
        client.post('/api/v1/wallet/debit',
            headers=auth_headers_student,
            json={
                "amount": 500,
                "purpose": "exam_purchase"
            }
        )
        
        wallet = test_db.wallets.find_one({"_id": ObjectId(test_user_student["wallet_id"])})
        assert wallet["version"] == initial_version + 2
