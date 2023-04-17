from __future__ import annotations

import logging
import uuid
from typing import Iterable

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
    ai_role: str = Field(help_text="The current ai task")

    class Config:
        arbitrary_types_allowed = True

    def filter_chat_gpt_commands(self, command_name: str | None = None, skip_first: bool = True) -> Iterable[tuple[int, GptResponse]]:
        """ gets all GptResponse message meeting all the criteria
        oldest with their message index
        :param command_name: filter for specific commands
        :param skip_first: if
        :return: tuple(message_index, GptResponse)
        """
        message_index = len(self.message_history) - 1
        skipped = not skip_first

        for message in reversed(self.message_history):
            if isinstance(message, GptResponse):
                matches = True
                if command_name and message.command != command_name:
                    matches = False

                if matches:
                    if not skipped:
                        skipped = True
                    else:
                        yield message_index, message

            message_index -= 1
