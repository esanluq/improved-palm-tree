import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Store original activities
    original_activities = activities.copy()
    yield
    # Reset activities after each test
    activities.clear()
    activities.update(original_activities)

def test_root_redirect(client):
    """Test that root endpoint redirects to index.html"""
    response = client.get("/")
    assert response.status_code in [200, 307]  # Accept both direct return and redirect
    if response.status_code == 307:
        assert response.headers["location"] == "/static/index.html"

def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()
    assert "Programming Class" in response.json()

def test_signup_success(client):
    """Test successful activity signup"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "new.student@mergington.edu"}
    )
    assert response.status_code == 200
    assert "new.student@mergington.edu" in activities["Chess Club"]["participants"]

def test_signup_already_registered(client):
    """Test signup when student is already registered"""
    # First signup
    client.post(
        "/activities/Chess Club/signup",
        params={"email": "test.student@mergington.edu"}
    )
    
    # Try to signup again
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "test.student@mergington.edu"}
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_activity_not_found(client):
    """Test signup for non-existent activity"""
    response = client.post(
        "/activities/NonExistentClub/signup",
        params={"email": "test.student@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_unregister_success(client):
    """Test successful unregistration from activity"""
    # First signup
    email = "test.unregister@mergington.edu"
    client.post(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    
    # Then unregister
    response = client.post(
        "/activities/Chess Club/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]

def test_unregister_not_found(client):
    """Test unregistration when student is not registered"""
    response = client.post(
        "/activities/Chess Club/unregister",
        params={"email": "nonexistent@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Student not found" in response.json()["detail"]

def test_unregister_activity_not_found(client):
    """Test unregistration from non-existent activity"""
    response = client.post(
        "/activities/NonExistentClub/unregister",
        params={"email": "test.student@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]