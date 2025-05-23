from typing import TypedDict


class UserInfo(TypedDict):
    user_id: str
    name: str
    age_range: str
    preferred_activities: list[str]
