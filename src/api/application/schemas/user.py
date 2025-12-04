from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class UserSchema:
    user_id: int
    short_name: str
    username: str
    number: int
