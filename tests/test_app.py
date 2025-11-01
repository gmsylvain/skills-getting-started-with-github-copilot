"""
Test suite for the Mergington High School Activities API

This module contains comprehensive tests for all API endpoints including:
- GET /activities
- POST /activities/{activity_name}/signup
- DELETE /activities/{activity_name}/unregister
- Root redirect functionality
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities data before each test to ensure test isolation."""
    # Store original activities
    original_activities = {
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
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Test cases for the root endpoint."""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Test cases for the GET /activities endpoint."""
    
    def test_get_activities_success(self, client, reset_activities):
        """Test successful retrieval of all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) >= 3  # At least the original 3 activities
        
        # Check specific activities exist
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        
        # Verify activity structure
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupEndpoint:
    """Test cases for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful student signup for an activity."""
        test_email = "test@mergington.edu"
        activity_name = "Chess Club"
        
        # Get initial participant count
        initial_participants = len(activities[activity_name]["participants"])
        
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Signed up {test_email} for {activity_name}"
        
        # Verify participant was added
        assert len(activities[activity_name]["participants"]) == initial_participants + 1
        assert test_email in activities[activity_name]["participants"]
    
    def test_signup_duplicate_participant(self, client, reset_activities):
        """Test that duplicate signup for same activity is prevented."""
        test_email = "michael@mergington.edu"  # Already registered for Chess Club
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is already signed up for this activity"
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity returns 404."""
        test_email = "test@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_with_encoded_activity_name(self, client, reset_activities):
        """Test signup works with URL-encoded activity names containing spaces."""
        test_email = "test@mergington.edu"
        activity_name = "Programming Class"
        encoded_activity = "Programming%20Class"
        
        response = client.post(f"/activities/{encoded_activity}/signup?email={test_email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Signed up {test_email} for {activity_name}"
        assert test_email in activities[activity_name]["participants"]


class TestUnregisterEndpoint:
    """Test cases for the DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful participant unregistration."""
        test_email = "michael@mergington.edu"  # Pre-registered for Chess Club
        activity_name = "Chess Club"
        
        # Verify participant is initially registered
        assert test_email in activities[activity_name]["participants"]
        initial_count = len(activities[activity_name]["participants"])
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={test_email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Unregistered {test_email} from {activity_name}"
        
        # Verify participant was removed
        assert test_email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1
    
    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregistering a participant who is not registered returns 400."""
        test_email = "notregistered@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={test_email}")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistering from non-existent activity returns 404."""
        test_email = "test@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={test_email}")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_with_encoded_activity_name(self, client, reset_activities):
        """Test unregistering works with URL-encoded activity names."""
        test_email = "emma@mergington.edu"  # Pre-registered for Programming Class
        activity_name = "Programming Class"
        encoded_activity = "Programming%20Class"
        
        response = client.delete(f"/activities/{encoded_activity}/unregister?email={test_email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Unregistered {test_email} from {activity_name}"
        assert test_email not in activities[activity_name]["participants"]


class TestCompleteWorkflow:
    """Integration tests for complete signup/unregister workflow."""
    
    def test_signup_then_unregister_workflow(self, client, reset_activities):
        """Test complete workflow: signup -> verify -> unregister -> verify."""
        test_email = "workflow@mergington.edu"
        activity_name = "Gym Class"
        
        # Step 1: Initial state - participant not registered
        assert test_email not in activities[activity_name]["participants"]
        initial_count = len(activities[activity_name]["participants"])
        
        # Step 2: Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert signup_response.status_code == 200
        assert test_email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1
        
        # Step 3: Try to sign up again (should fail)
        duplicate_response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert duplicate_response.status_code == 400
        
        # Step 4: Unregister
        unregister_response = client.delete(f"/activities/{activity_name}/unregister?email={test_email}")
        assert unregister_response.status_code == 200
        assert test_email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count
        
        # Step 5: Try to unregister again (should fail)
        duplicate_unregister = client.delete(f"/activities/{activity_name}/unregister?email={test_email}")
        assert duplicate_unregister.status_code == 400
    
    def test_multiple_activities_signup(self, client, reset_activities):
        """Test that a student can sign up for multiple different activities."""
        test_email = "multisport@mergington.edu"
        
        # Sign up for multiple activities
        activities_to_join = ["Chess Club", "Programming Class", "Gym Class"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={test_email}")
            assert response.status_code == 200
            assert test_email in activities[activity]["participants"]
        
        # Verify participant is in all activities
        for activity in activities_to_join:
            assert test_email in activities[activity]["participants"]


class TestDataIntegrity:
    """Test data integrity and edge cases."""
    
    def test_activities_data_structure_integrity(self, client, reset_activities):
        """Test that activities maintain proper data structure after operations."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            # Verify required fields exist
            required_fields = ["description", "schedule", "max_participants", "participants"]
            for field in required_fields:
                assert field in activity_data, f"Missing field {field} in {activity_name}"
            
            # Verify data types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            
            # Verify participant count doesn't exceed maximum
            assert len(activity_data["participants"]) <= activity_data["max_participants"]
    
    def test_email_parameter_handling(self, client, reset_activities):
        """Test various email parameter formats and edge cases."""
        activity_name = "Chess Club"
        
        # Test normal email
        normal_email = "test@mergington.edu"
        response = client.post(f"/activities/{activity_name}/signup?email={normal_email}")
        assert response.status_code == 200
        
        # Clean up
        client.delete(f"/activities/{activity_name}/unregister?email={normal_email}")
        
        # Test email with special characters (URL encoded)
        special_email = "test+special@mergington.edu"
        encoded_email = "test%2Bspecial%40mergington.edu"
        response = client.post(f"/activities/{activity_name}/signup?email={encoded_email}")
        assert response.status_code == 200
        
        # Verify the decoded email is stored
        assert special_email in activities[activity_name]["participants"]