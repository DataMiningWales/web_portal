import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.models.subscription import SubscriptionRequest


client = TestClient(app)


@pytest.fixture
def mock_db_service():
    with patch('app.services.database.db_service') as mock:
        mock.check_existing_subscription = AsyncMock(return_value=None)
        mock.create_subscription = AsyncMock(return_value="test-uuid-123")
        yield mock


@pytest.fixture
def mock_email_service():
    with patch('app.services.email.email_service') as mock:
        mock.send_subscription_acknowledgment = AsyncMock(return_value=True)
        mock.send_admin_notification = AsyncMock(return_value=True)
        yield mock


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Data Mining Wales Subscription API" in response.json()["message"]


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_subscription_success(mock_db_service, mock_email_service):
    """Test successful subscription creation"""
    subscription_data = {
        "email": "test@example.com",
        "name": "Test User",
        "organization": "Test Org",
        "interests": "Data Mining"
    }
    
    response = client.post("/api/v1/subscriptions/", json=subscription_data)
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "pending"
    assert "request_id" in response_data
    assert "pending approval" in response_data["message"]


@pytest.mark.asyncio
async def test_create_subscription_duplicate(mock_db_service, mock_email_service):
    """Test duplicate subscription rejection"""
    # Mock existing subscription
    from app.models.subscription import Subscription, SubscriptionStatus
    from datetime import datetime
    
    existing_subscription = Subscription(
        request_id="existing-123",
        email="test@example.com",
        status=SubscriptionStatus.PENDING,
        created_at=datetime.utcnow()
    )
    
    mock_db_service.check_existing_subscription.return_value = existing_subscription
    
    subscription_data = {
        "email": "test@example.com",
        "name": "Test User"
    }
    
    response = client.post("/api/v1/subscriptions/", json=subscription_data)
    
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_admin_login_success():
    """Test successful admin login"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = client.post("/api/v1/admin/login", json=login_data)
    
    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"


def test_admin_login_invalid_credentials():
    """Test admin login with invalid credentials"""
    login_data = {
        "username": "admin",
        "password": "wrong-password"
    }
    
    response = client.post("/api/v1/admin/login", json=login_data)
    
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_subscription_validation():
    """Test subscription request validation"""
    # Test invalid email
    invalid_data = {
        "email": "not-an-email",
        "name": "Test User"
    }
    
    response = client.post("/api/v1/subscriptions/", json=invalid_data)
    assert response.status_code == 422  # Validation error


def test_missing_email():
    """Test subscription request without email"""
    invalid_data = {
        "name": "Test User",
        "organization": "Test Org"
    }
    
    response = client.post("/api/v1/subscriptions/", json=invalid_data)
    assert response.status_code == 422  # Validation error