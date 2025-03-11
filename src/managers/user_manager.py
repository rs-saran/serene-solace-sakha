import uuid
from typing import List, Optional, Union
from src.managers.postgres_db_manager import PostgresDBManager 

class UserManager:
    def __init__(self):
        self.db = PostgresDBManager()

    def add_user(self, name: str, age_range: str, preferred_activities: List[str]) -> str:
        """Creates a new user with a unique UUID and stores it in the database."""
        user_id = str(uuid.uuid4())  # Generate a random UUID
        query = """
        INSERT INTO users (user_id, name, age_range, preferred_activities)
        VALUES (%s, %s, %s, %s);
        """
        try:
            self.db.execute(query, (user_id, name, age_range, preferred_activities))
            return user_id  # Return the generated user ID
        except Exception as e:
            print(f"Error adding user: {e}")
            return None

    def get_user_info(self, user_id: str) -> Optional[dict]:
        """Fetches a user by ID, handling cases where the user is not found."""
        if not user_id:
            print("Error: Missing user ID")
            return None

        query = "SELECT user_id, name, age_range, preferred_activities FROM users WHERE user_id = %s;"
        result = self.db.execute(query, (user_id,), fetch=True)

        if result:
            return {
                "user_id": result[0][0],
                "name": result[0][1],
                "age_range": result[0][2],
                "preferred_activities": result[0][3],
            }

        print(f"User with ID {user_id} not found.")
        return None

    def get_user_session_count(self, user_id: str) -> Optional[dict]:
        """Fetches a user by ID, handling cases where the user is not found."""
        if not user_id:
            print("Error: Missing user ID")
            return None

        query = "SELECT user_id, session_count FROM users WHERE user_id = %s;"
        result = self.db.execute(query, (user_id,), fetch=True)

        if result:
            return {
                "user_id": result[0][0],
                "session_count": result[0][1],
            }
            
        print(f"User with ID {user_id} not found.")
        return None

    def get_all_users(self) -> List[dict]:
        """Fetches all users from the database."""
        query = "SELECT * FROM users;"
        result = self.db.execute(query, fetch=True)

        if not result:
            print("No users found.")
            return []

        return [
            {
                "user_id": row[0],
                "name": row[1],
                "age_range": row[2],
                "preferred_activities": row[3],
                "created_at": row[4]
            }
            for row in result
        ]

    def update_user_activities(self, user_id: str, new_activities: List[str]) -> bool:
        """Updates a user's preferred activities, ensuring the user exists."""
        if not user_id:
            print("Error: Missing user ID")
            return False

        existing_user = self.get_user(user_id)
        if not existing_user:
            return False

        query = "UPDATE users SET preferred_activities = %s WHERE user_id = %s;"
        try:
            self.db.execute(query, (new_activities, user_id))
            return True
        except Exception as e:
            print(f"Error updating activities: {e}")
            return False

    def delete_user(self, user_id: str) -> bool:
        """Deletes a user if they exist."""
        if not user_id:
            print("Error: Missing user ID")
            return False

        existing_user = self.get_user(user_id)
        if not existing_user:
            return False

        query = "DELETE FROM users WHERE user_id = %s;"
        try:
            self.db.execute(query, (user_id,))
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False