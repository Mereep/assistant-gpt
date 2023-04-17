from __future__ import annotations

import datetime
from typing import Any

from pydantic import BaseModel, Field


class GptResponse(BaseModel):
    plan: str | None = Field(help_text="Plan of action / thoughts")
    steps: list[str] | str = Field(help_text="Steps to take", default_factory=list)
    command: str = Field(help_text="Command to use")
    arguments: dict[str, Any] | None = Field(help_text="Arguments for the command")
    created_ts: int = Field(default_factory=lambda: datetime.datetime.now().timestamp())
    # next_step: str = Field()
    # critic: str | None = Field(help_text="Possible Criticism of the plan")

    # name: str | None = Field(help_text="Name of the response")
