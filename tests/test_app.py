"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for interscholastic games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu", "james@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in school plays and theatrical productions",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        },
        "Visual Arts": {
            "description": "Painting, drawing, and sculpture classes",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore science experiments and participate in science fairs",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ethan@mergington.edu", "noah@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Advanced mathematics problem-solving and competitions",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["grace@mergington.edu"]
        }
    }
    
    # Clear and restore activities
    activities.clear()
    activities.update(original)
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original)


class TestGetActivities:
    """Test the GET /activities endpoint"""

    def test_get_activities_returns_200(self, client, reset_activities):
        """Test that getting activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client, reset_activities):
        """Test that getting activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_all_activities(self, client, reset_activities):
        """Test that all activities are returned"""
        response = client.get("/activities")
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Math Olympiad" in data

    def test_activity_has_required_fields(self, client, reset_activities):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_returns_200(self, client, reset_activities):
        """Test that signup returns a 200 status code"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup adds a participant to the activity"""
        email = "newstudent@mergington.edu"
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        
        assert response.status_code == 200
        assert "Chess Club" in activities
        assert email in activities["Chess Club"]["participants"]

    def test_signup_returns_success_message(self, client, reset_activities):
        """Test that signup returns a success message"""
        email = "newstudent@mergington.edu"
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_for_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that signup for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_email_returns_400(self, client, reset_activities):
        """Test that signup with duplicate email returns 400"""
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestRemoveParticipant:
    """Test the DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_remove_participant_returns_200(self, client, reset_activities):
        """Test that removing a participant returns 200"""
        email = "michael@mergington.edu"
        response = client.delete(f"/activities/Chess Club/participants/{email}")
        assert response.status_code == 200

    def test_remove_participant_removes_from_activity(self, client, reset_activities):
        """Test that removing a participant removes them from the activity"""
        email = "michael@mergington.edu"
        response = client.delete(f"/activities/Chess Club/participants/{email}")
        
        assert response.status_code == 200
        assert email not in activities["Chess Club"]["participants"]

    def test_remove_participant_returns_message(self, client, reset_activities):
        """Test that removing a participant returns a message"""
        email = "michael@mergington.edu"
        response = client.delete(f"/activities/Chess Club/participants/{email}")
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]

    def test_remove_from_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that removing from nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Activity/participants/student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_remove_nonexistent_participant_returns_400(self, client, reset_activities):
        """Test that removing nonexistent participant returns 400"""
        response = client.delete(
            "/activities/Chess Club/participants/nonexistent@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_remove_participant_frees_up_spot(self, client, reset_activities):
        """Test that removing a participant frees up a spot"""
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        initial_count = len(activities[activity_name]["participants"])
        
        # Remove
        client.delete(f"/activities/{activity_name}/participants/{email}")
        final_count = len(activities[activity_name]["participants"])
        
        assert final_count == initial_count - 1


class TestRootEndpoint:
    """Test the root endpoint"""

    def test_root_returns_redirect(self, client):
        """Test that root endpoint returns a redirect"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
