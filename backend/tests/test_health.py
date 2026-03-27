"""
Tests for health check endpoint.
"""
import pytest


class TestHealthEndpoint:
    """Tests for /health endpoint."""
    
    def test_health_check_returns_200(self, client):
        """Test that health check returns 200 status."""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_check_returns_success_true(self, client):
        """Test that health check returns success=True."""
        response = client.get("/health")
        data = response.get_json()
        assert data["success"] is True
    
    def test_health_check_returns_message(self, client):
        """Test that health check returns proper message."""
        response = client.get("/health")
        data = response.get_json()
        assert data["message"] == "ExamSaaS API is running"
    
    def test_health_check_returns_version(self, client):
        """Test that health check returns version info."""
        response = client.get("/health")
        data = response.get_json()
        assert "version" in data["data"]
        assert data["data"]["version"] == "1.0.0"
    
    def test_health_check_returns_env(self, client):
        """Test that health check returns environment info."""
        response = client.get("/health")
        data = response.get_json()
        assert "env" in data["data"]
