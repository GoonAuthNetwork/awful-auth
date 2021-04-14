from datetime import datetime
from typing import Optional
from urllib import parse
from pydantic import BaseModel, Field


class GoonAuthBase(BaseModel):
    user_name: str = Field(
        ..., title="SA Username", min_length=3, max_length=18, regex="^[\x00-\x7F]+$"
    )

    def user_name_sanitized(self):
        return parse.quote(self.user_name)


class GoonAuthRequest(GoonAuthBase):
    pass


class GoonAuthChallenge(GoonAuthBase):
    hash: str = Field(title="Hash the user is required to place in profile")


class GoonAuthStatus(BaseModel):
    validated: bool = Field(..., title="If the user is validated or not")

    # Simple information about the user from their profile
    user_name: Optional[str] = Field(
        None, title="SA Username", min_length=3, max_length=18, regex="^[\x00-\x7F]+$"
    )
    user_id: Optional[int] = Field(None, title="SA User Id", gt=0)
    register_date: Optional[datetime] = Field(None, title="SA register date")
    permabanned: Optional[datetime] = Field(
        None, title="Date of if/when the user is permanently banned on SA"
    )
