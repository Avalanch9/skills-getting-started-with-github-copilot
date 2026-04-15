"""Unit tests for business logic using AAA pattern."""

import pytest
from src.app import activities, app


class TestActivityDataStructure:
    """Tests for activity data structure and validation."""

    def test_activity_has_required_fields(self):
        """Test that each activity has all required fields."""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act & Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict), f"{activity_name} should be a dict"
            assert required_fields.issubset(activity_data.keys()), \
                f"{activity_name} missing required fields"
            assert isinstance(activity_data["participants"], list), \
                f"{activity_name} participants should be a list"

    def test_max_participants_is_positive(self):
        """Test that all activities have positive max_participants."""
        # Arrange & Act
        for activity_name, activity_data in activities.items():
            # Assert
            assert activity_data["max_participants"] > 0, \
                f"{activity_name} max_participants must be positive"

    def test_participants_are_valid_emails(self):
        """Test that participants are stored as strings (emails)."""
        # Arrange & Act
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                # Assert
                assert isinstance(participant, str), \
                    f"Participant in {activity_name} should be a string"
                assert "@" in participant, \
                    f"Participant in {activity_name} should be an email format"


class TestParticipantBusinessLogic:
    """Tests for participant management business logic."""

    def test_participant_not_duplicated_in_list(self, reset_activities):
        """Test that a participant doesn't appear twice in the list."""
        # Arrange
        activity_name = "Chess Club"
        initial_participants = activities[activity_name]["participants"].copy()
        
        # Act & Assert
        assert len(initial_participants) == len(set(initial_participants)), \
            "Participants list should not contain duplicates"

    def test_available_spots_calculation(self, reset_activities):
        """Test that available spots can be correctly calculated."""
        # Arrange
        activity_name = "Chess Club"
        activity_data = activities[activity_name]
        max_participants = activity_data["max_participants"]
        current_participants = len(activity_data["participants"])
        
        # Act
        available_spots = max_participants - current_participants
        
        # Assert
        assert available_spots >= 0, "Available spots should never be negative"
        assert available_spots == max_participants - current_participants

    def test_signup_increases_participant_count(self, reset_activities):
        """Test that manually adding a participant increases the count."""
        # Arrange
        activity_name = "Art Club"
        email = "new_artist@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        activities[activity_name]["participants"].append(email)
        
        # Assert
        assert len(activities[activity_name]["participants"]) == initial_count + 1
        assert email in activities[activity_name]["participants"]

    def test_unregister_decreases_participant_count(self, reset_activities):
        """Test that removing a participant decreases the count."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        activities[activity_name]["participants"].remove(email)
        
        # Assert
        assert len(activities[activity_name]["participants"]) == initial_count - 1
        assert email not in activities[activity_name]["participants"]


class TestErrorConditions:
    """Tests for error conditions and edge cases."""

    def test_activity_not_found_error(self):
        """Test that looking up nonexistent activity returns False."""
        # Arrange
        nonexistent_activity = "Fake Activity"
        
        # Act & Assert
        assert nonexistent_activity not in activities

    def test_duplicate_signup_detection(self, reset_activities):
        """Test that duplicate participant can be detected."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act & Assert
        assert email in activities[activity_name]["participants"]
        assert activities[activity_name]["participants"].count(email) == 1

    def test_unregister_nonexistent_participant(self, reset_activities):
        """Test that removing nonexistent participant raises error."""
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = "nonexistent@mergington.edu"
        
        # Act & Assert
        with pytest.raises(ValueError):
            activities[activity_name]["participants"].remove(nonexistent_email)
