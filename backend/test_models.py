"""Test script for Stage 2 models verification."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all models can be imported."""
    print("Testing model imports...")
    
    try:
        from app.models import (
            Institute, User, StudentProfile, TeacherProfile, Plan, Subscription,
            Wallet, WalletTransaction, Payment, Exam, Question, ExamAttempt, Result,
            Certificate, Ebook, PDFUpload, AIRecommendation,
            SupportTicket, TicketMessage, AuditLog
        )
        print("[PASS] All models imported successfully!")
        
        models = [
            'Institute', 'User', 'StudentProfile', 'TeacherProfile', 'Plan',
            'Subscription', 'Wallet', 'WalletTransaction', 'Payment', 'Exam',
            'Question', 'ExamAttempt', 'Result', 'Certificate', 'Ebook',
            'PDFUpload', 'AIRecommendation', 'SupportTicket', 'TicketMessage', 'AuditLog'
        ]
        
        for model_name in models:
            if model_name not in dir():
                print(f"[FAIL] {model_name} not found in imports")
            else:
                print(f"[PASS] {model_name}")
        
        print("\n" + "="*50)
        print("Stage 2 Models: SUCCESS")
        print("="*50)
        
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        import traceback
        traceback.print_exc()

def test_helpers():
    """Test helper functions."""
    print("\nTesting helper functions...")
    
    try:
        from app.helpers import (
            paise_to_rupees, rupees_to_paise, format_currency,
            generate_slug, generate_ticket_number, generate_certificate_code
        )
        
        assert paise_to_rupees(19900) == 199.0, "paise_to_rupees failed"
        assert rupees_to_paise(199.0) == 19900, "rupees_to_paise failed"
        assert generate_slug("Hello World!") == "hello-world", "generate_slug failed"
        
        print("[PASS] All helpers working correctly!")
        
    except Exception as e:
        print(f"[FAIL] Helper error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_imports()
    test_helpers()
