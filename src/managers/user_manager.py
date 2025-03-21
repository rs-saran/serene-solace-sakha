import uuid
from typing import Dict, List, Optional

from src.logger import get_logger
from src.managers.postgres_db_manager import PostgresDBManager

logger = get_logger(__name__)


class UserManager:
    def __init__(self, db_manager: PostgresDBManager):
        """Initialize the UserManager with a database connection."""
        self.db = db_manager

    def add_user(
        self, name: str, age_range: str, preferred_activities: List[str]
    ) -> Optional[str]:
        """Creates a new user with a unique UUID and stores it in the database."""
        user_id = str(uuid.uuid4())  # Generate a random UUID
        query = """
        INSERT INTO users (user_id, name, age_range, preferred_activities)
        VALUES (%s, %s, %s, %s);
        """
        try:
            self.db.execute(query, (user_id, name, age_range, preferred_activities))
            logger.info(f"User {name} added successfully with ID {user_id}.")
            return user_id
        except Exception as e:
            logger.error(f"Error adding user: {e}", exc_info=True)
            return None

    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """Fetches a user by ID, returning None if not found."""
        if not user_id:
            logger.error("Error: Missing user ID")
            return None

        query = "SELECT user_id, name, age_range, preferred_activities FROM users WHERE user_id = %s;"
        try:
            result = self.db.execute(query, (user_id,), fetch=True)
            if result:
                return {
                    "user_id": result[0][0],
                    "name": result[0][1],
                    "age_range": result[0][2],
                    "preferred_activities": result[0][3],
                }
            logger.warning(f"User with ID {user_id} not found.")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user info: {e}", exc_info=True)
            return None

    def get_user_session_count(self, user_id: str) -> Optional[Dict]:
        """Fetches a user's session count by ID."""
        if not user_id:
            logger.error("Error: Missing user ID")
            return None

        query = "SELECT session_count FROM users WHERE user_id = %s;"
        try:
            result = self.db.execute(query, (user_id,), fetch=True)
            if result:
                return result[0][0]
            logger.warning(f"User with ID {user_id} not found.")
            return None
        except Exception as e:
            logger.error(f"Error retrieving session count: {e}", exc_info=True)
            return None

    def get_all_users(self) -> List[Dict]:
        """Fetches all users from the database."""
        query = "SELECT * FROM users;"
        try:
            result = self.db.execute(query, fetch=True)
            if not result:
                logger.info("No users found in the database.")
                return []

            return [
                {
                    "user_id": row[0],
                    "name": row[1],
                    "age_range": row[2],
                    "preferred_activities": row[3],
                    "created_at": row[4],
                }
                for row in result
            ]
        except Exception as e:
            logger.error(f"Error retrieving users: {e}", exc_info=True)
            return []

    def start_user_session(self, user_id: str):
        """Increments the session count for the user by 1."""
        if not user_id:
            logger.error("Error: Missing user ID")
            return False

        # Check if user exists first
        current_session_count = self.get_user_session_count(user_id)
        new_session_count = int(current_session_count) + 1

        query = "UPDATE users SET session_count = %s WHERE user_id = %s;"
        try:
            self.db.execute(query, (new_session_count, user_id))
            logger.info(f"Incremented session count for user {user_id} to {new_session_count}.")
            return new_session_count
        except Exception as e:
            logger.error(f"Error updating session count: {e}", exc_info=True)
            return None


    def update_user_activities(self, user_id: str, new_activities: List[str]) -> bool:
        """Updates a user's preferred activities if they exist."""
        if not user_id:
            logger.error("Error: Missing user ID")
            return False

        if not self.get_user_info(user_id):
            logger.warning(f"Update failed: User {user_id} not found.")
            return False

        query = "UPDATE users SET preferred_activities = %s WHERE user_id = %s;"
        try:
            self.db.execute(query, (new_activities, user_id))
            logger.info(f"Updated activities for user {user_id}.")
            return True
        except Exception as e:
            logger.error(f"Error updating activities: {e}", exc_info=True)
            return False

    def delete_user(self, user_id: str) -> bool:
        """Deletes a user if they exist."""
        if not user_id:
            logger.error("Error: Missing user ID")
            return False

        if not self.get_user_info(user_id):
            logger.warning(f"Delete failed: User {user_id} not found.")
            return False

        query = "DELETE FROM users WHERE user_id = %s;"
        try:
            self.db.execute(query, (user_id,))
            logger.info(f"User {user_id} deleted successfully.")
            return True
        except Exception as e:
            logger.error(f"Error deleting user: {e}", exc_info=True)
            return False
