from __future__ import annotations

import logging
import uuid

from pydantic import Field, BaseModel

from datatypes.gpt_response import GptResponse
from datatypes.user_message import UserMessage
from repository.i_file_storage_backend import IFileStorageBackend
from repository.i_key_storage_backend import IKeyStorageBackend
from utils.app_settings import AppSettings


class ChatContext(BaseModel):
    bot_name: str = Field(help_text="The name of the bot", default="Assistant")
    active_user: str = Field(help_text="The active user")
    users: list[str] = Field(help_text="The list of users", default_factory=lambda: ["User"])

    conversation_id: str = Field(help_text="The id of the conversation",
                                 default_factory=lambda: uuid.uuid4().__str__())

    message_history: list[GptResponse | UserMessage] = Field(help_text="The history of messages",
                                                             default_factory=list)

    key_storage_backend: IKeyStorageBackend = Field(help_text="The storage backend to use for key value pairs")
    file_storage_backend: IFileStorageBackend = Field(help_text="The storage backend to use for files")

    settings: AppSettings = Field(help_text="The Application Settings")
    default_logger: logging.Logger = Field(help_text="The default logger")


    class Config:
        arbitrary_types_allowed = True

