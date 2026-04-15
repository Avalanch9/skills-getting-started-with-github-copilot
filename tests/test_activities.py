"""Integration tests for the activities API endpoints using AAA pattern."""

import pytest
from urllib.parse import quote


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned with correct structure."""
        # Arrange
        # Client is already set up with test data
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_get_activities_returns_correct_structure(self, client):
        """Test that activity objects have required fields."""
        # Arrange
        # Client is already set up
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]
        
        # Assert
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_includes_existing_participants(self, client):
        """Test that activities with participants show them correctly."""
        # Arrange
        # Reset activities has Chess Club with participants
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        chess_club_participants = activities["Chess Club"]["participants"]
        assert "michael@mergington.edu" in chess_club_participants
        assert "daniel@mergington.edu" in chess_club_participants
        assert len(chess_club_participants) == 2


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful_with_available_spots(self, client):
        """Test that a student can successfully sign up for an activity with spots available."""
        # Arrange
        activity_name = "Soccer Team"
        email = "alex@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            json={}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_fails_for_nonexistent_activity(self, client):
        """Test that signup fails with 404 when activity doesn't exist."""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "alex@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            json={}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_fails_when_already_signed_up(self, client):
        """Test that signup fails with 400 when student already signed up."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            json={}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup correctly adds participant to activity's list."""
        # Arrange
        activity_name = "Art Club"
        email = "new_student@mergington.edu"
        response_before = client.get("/activities")
        activities_before = response_before.json()
        initial_count = len(activities_before[activity_name]["participants"])
        
        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}", json={})
        
        # Assert
        response_after = client.get("/activities")
        activities_after = response_after.json()
        assert len(activities_after[activity_name]["participants"]) == initial_count + 1
        assert email in activities_after[activity_name]["participants"]

    def test_signup_with_url_encoded_email(self, client):
        """Test that signup handles special characters in email properly."""
        # Arrange
        activity_name = "Soccer Team"
        email = "alex+test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={quote(email)}",
            json={}
        )
        
        # Assert
        assert response.status_code == 200
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_successful_removes_participant(self, client):
        """Test that unregister successfully removes a participant from an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}",
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_fails_for_nonexistent_activity(self, client):
        """Test that unregister fails with 404 when activity doesn't exist."""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}",
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_fails_when_not_signed_up(self, client):
        """Test that unregister fails with 400 when student not signed up."""
        # Arrange
        activity_name = "Chess Club"
        email = "not_signed_up@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}",
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_unregister_decreases_participant_count(self, client):
        """Test that unregister correctly decreases the participant count."""
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        response_before = client.get("/activities")
        activities_before = response_before.json()
        initial_count = len(activities_before[activity_name]["participants"])
        
        # Act
        client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        # Assert
        response_after = client.get("/activities")
        activities_after = response_after.json()
        assert len(activities_after[activity_name]["participants"]) == initial_count - 1
        assert email not in activities_after[activity_name]["participants"]

    def test_unregister_specific_participant_only(self, client):
        """Test that unregister only removes the specified participant."""
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        email_to_keep = "daniel@mergington.edu"
        
        # Act
        client.delete(f"/activities/{activity_name}/unregister?email={email_to_remove}")
        
        # Assert
        response = client.get("/activities")
        activities = response.json()
        assert email_to_remove not in activities[activity_name]["participants"]
        assert email_to_keep in activities[activity_name]["participants"]


class TestActivitySignupAndUnregisterFlow:
    """Integration tests for complete signup and unregister workflows."""

    def test_signup_then_unregister_flow(self, client):
        """Test complete flow of signing up and then unregistering."""
        # Arrange
        activity_name = "Drama Club"
        email = "student@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            json={}
        )
        
        # Assert signup worked
        assert signup_response.status_code == 200
        activities_after_signup = client.get("/activities").json()
        assert email in activities_after_signup[activity_name]["participants"]
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}",
        )
        
        # Assert unregister worked
        assert unregister_response.status_code == 200
        activities_after_unregister = client.get("/activities").json()
        assert email not in activities_after_unregister[activity_name]["participants"]

    def test_multiple_students_signup_and_unregister(self, client):
        """Test that multiple students can sign up and unregister independently."""
        # Arrange
        activity_name = "Swimming Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        email3 = "student3@mergington.edu"
        
        # Act - Multiple sign ups
        client.post(f"/activities/{activity_name}/signup?email={email1}", json={})
        client.post(f"/activities/{activity_name}/signup?email={email2}", json={})
        client.post(f"/activities/{activity_name}/signup?email={email3}", json={})
        
        # Assert all signed up
        activities = client.get("/activities").json()
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]
        assert email3 in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 3
        
        # Act - Remove one
        client.delete(f"/activities/{activity_name}/unregister?email={email2}")
        
        # Assert only email2 removed
        activities = client.get("/activities").json()
        assert email1 in activities[activity_name]["participants"]
        assert email2 not in activities[activity_name]["participants"]
        assert email3 in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 2
