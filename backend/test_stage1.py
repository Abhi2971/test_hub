"""Quick test script for Stage 1 verification."""
import sys
sys.path.insert(0, '.')

from app import create_app
from app.config import Config

def test_health():
    config = Config.from_env()
    app = create_app(config)
    
    print("App created successfully!")
    print("Testing /health endpoint...")
    
    client = app.test_client()
    response = client.get('/health')
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.get_json()}")
    
    data = response.get_json()
    
    # Verify response structure
    assert data['success'] == True, "success should be True"
    assert data['message'] == "ExamSaaS API is running", "message mismatch"
    assert 'version' in data['data'], "version missing"
    assert 'env' in data['data'], "env missing"
    
    print("\n[PASS] All health check tests passed!")
    
    # Test error responses using test client
    print("\nTesting error response...")
    response = client.post('/nonexistent')
    error_data = response.get_json()
    assert error_data['success'] == False
    print(f"Error response: {error_data}")
    print("[PASS] Error response test passed!")
    
    print("\n" + "="*50)
    print("Stage 1 Verification: SUCCESS")
    print("="*50)

if __name__ == "__main__":
    test_health()
