from datetime import datetime
from typing import Optional
from urllib import parse
from pydantic import BaseModel, Field


class GoonAuthBase(BaseModel):
    user_name: str = Field(
        ...,
        title="Something Awful username",
        min_length=3,
        max_length=100,
        # TODO: Reimplement validation once userid api is added.
        # Thanks SA for having absolutely no standards for valid usernames.
        # max_length=50,
        # regex="^[a-zA-Z0-9-_ ]{3,50}$",
    )

    def user_name_sanitized(self):
        return parse.quote(self.user_name)


class GoonAuthRequest(GoonAuthBase):
    pass


class GoonAuthChallenge(GoonAuthBase):
    hash: str = Field(title="Hash the user is required to place in their profile")


class GoonAuthStatus(BaseModel):
    validated: bool = Field(..., title="If the user is validated or not")

    # Simple information about the user from their profile
    user_name: Optional[str] = Field(
        None,
        title="Something Awful username",
        min_length=3,
        max_length=100
        # TODO: Reimplement validation once userid api is added.
        # Thanks SA for having absolutely no standards for valid usernames.
        # max_length=50,
        # regex="^[a-zA-Z0-9-_ ]{3,50}$",
    )
    user_id: Optional[int] = Field(None, title="Something Awful user id", gt=0)
    register_date: Optional[datetime] = Field(
        None, title="Something Awful register date"
    )
    permabanned: Optional[datetime] = Field(
        None, title="Date of if/when the user was permanently banned"
    )
