from __future__ import annotations

from pydantic import BaseModel, Field


class UserMessage(BaseModel):
    user_response: str = Field(help_text="The users response message")
    additional_info: str | None = Field(
        help_text="Additional information", default=None
    )
    user: str = Field(help_text="The user who sent the message")
