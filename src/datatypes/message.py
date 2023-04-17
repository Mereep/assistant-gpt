from typing import Any

from pydantic import BaseModel, Field

from datatypes.gpt_response import GptResponse


class Message(BaseModel):
    actor: str = Field(help_text="Who sends the message?")
    message: GptResponse = Field(help_text="The message itself")
