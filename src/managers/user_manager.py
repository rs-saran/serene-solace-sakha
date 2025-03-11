import uuid
from typing import List, Optional, Union
from postgres_db_manager import PostgresDBManager  # Ensure correct import

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
            return ""

    def get_user(self, user_id: str) -> Optional[dict]:
        """Fetches a user by ID, handling cases where the user is not found."""
        if not user_id:
            print("Error: Missing user ID")
            return None

        query = "SELECT * FROM users WHERE user_id = %s;"
        result = self.db.execute(query, (user_id,), fetch=True)

        if result:
            return {
                "user_id": result[0][0],
                "name": result[0][1],
                "age_range": result[0][2],
                "preferred_activities": result[0][3],
                "created_at": result[0][4]
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


# # Example Usage
# if __name__ == "__main__":
#     user_manager = UserManager()

#     # Add a new user
#     new_user_id = user_manager.add_user("John Doe", "30-40", ["Reading", "Traveling", "Cooking"])
#     print(f"Added User ID: {new_user_id}")

#     # Fetch a user
#     user = user_manager.get_user(new_user_id)
#     print("User Data:", user)

#     # Handle missing or invalid user ID
#     user_not_found = user_manager.get_user("invalid-id")
#     print("Invalid User Lookup:", user_not_found)

#     # Fetch all users
#     users = user_manager.get_all_users()
#     print("All Users:", users)

#     # Update user activities
#     updated = user_manager.update_user_activities(new_user_id, ["Cycling", "Gaming"])
#     print(f"User activities updated: {updated}")

#     # Attempt to delete a non-existent user
#     deleted = user_manager.delete_user("invalid-id")
#     print(f"Deleted invalid user: {deleted}")

#     # Delete an actual user
#     deleted_real = user_manager.delete_user(new_user_id)
#     print(f"Deleted real user: {deleted_real}")
