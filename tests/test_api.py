from fastapi.testclient import TestClient
from app.main import app
from app.services.ai_agent import AIAgent
from unittest.mock import AsyncMock, patch
import pytest

# Create a test client
client = TestClient(app)

# Mock responses
MOCK_OLLAMA_RESPONSE = "This is a mock response from Ollama"

@pytest.fixture
def mock_ollama():
    """Fixture to mock Ollama service"""
    with patch('app.services.ollama_service.AsyncClient') as mock_client:
        # Mock the generate method
        mock_client.return_value.generate = AsyncMock(
            return_value={"response": MOCK_OLLAMA_RESPONSE}
        )
        # Mock the list method for health checks
        mock_client.return_value.list = AsyncMock(
            return_value={"models": [{"name": "deepscaler"}]}
        )
        yield mock_client

def test_read_root(mock_ollama):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_read_status(mock_ollama):
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    assert "status" in response.json()
    assert "version" in response.json()

def test_chat_endpoint(mock_ollama):
    test_message = "Hello, AI!"
    response = client.post(
        "/api/v1/chat",
        json={"message": test_message}
    )
    assert response.status_code == 200
    assert "response" in response.json()
    assert "timestamp" in response.json()
    assert response.json()["response"] == MOCK_OLLAMA_RESPONSE

def test_chat_endpoint_empty_message(mock_ollama):
    response = client.post(
        "/api/v1/chat",
        json={"message": ""}
    )
    assert response.status_code == 422  # Validation error

def test_chat_endpoint_invalid_json(mock_ollama):
    response = client.post(
        "/api/v1/chat",
        json={"invalid_field": "test"}
    )
    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_ollama_service_failure():
    """Test handling of Ollama service failure"""
    with patch('app.services.ollama_service.AsyncClient') as mock_client:
        # Mock a failed response
        mock_client.return_value.generate = AsyncMock(side_effect=Exception("Ollama service error"))
        mock_client.return_value.list = AsyncMock(return_value={"models": []})
        
        response = client.post(
            "/api/v1/chat",
            json={"message": "Hello"}
        )
        assert response.status_code == 503  # Service Unavailable 