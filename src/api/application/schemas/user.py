from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class UserSchema:
    user_id: int
    username: str
    number: int
