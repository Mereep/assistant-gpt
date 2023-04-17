import json
import logging

from datatypes.chat_context import ChatContext
from exceptions.conversation_exception import (
    ConversationCannotBeSavedException,
    ConversationNotReadableException,
)
from utils.app_settings import AppSettings
from utils.storage import load_key_storage_backend, load_file_storage_backend


def available_conversations(app_settings: AppSettings) -> list[str]:
    """Returns a list of all available conversations
    Args:
        app_settings: the application settings (will be used to determine the conversation path)
    """
    conversations = []
    for f in app_settings.conversation_path.iterdir():
        if f.is_dir() and f / "conversation.json" in f.iterdir():
            conversations.append(f.name)

    return conversations


def save_conversation(ctx: ChatContext):
    """Saves a conversation to the file system
    Args:
        ctx: the chat context to save will save in conversation_path / conversation_id
    raises:
        ConversationCannotBeSavedException: if the conversation cannot be saved
    """
    conversation_path = ctx.settings.conversation_path / ctx.conversation_id
    conversation_path.mkdir(exist_ok=True)
    json = ctx.json(
        exclude={
            "file_storage_backend",
            "key_storage_backend",
            "settings",
            "default_logger",
        },
        indent=4,
        sort_keys=True,
    )
    try:
        with open(conversation_path / "conversation.json", "w") as f:
            f.write(json)
    except Exception as e:
        raise ConversationCannotBeSavedException(
            f"Couldn't save conversation due to `{str(e)}`"
        )


def load_conversation(
    conversation_id: str, app_settings: AppSettings, logger: logging.Logger
) -> ChatContext:
    """Loads a conversation from the file system
    Args:
        conversation_id: the id of the conversation to load
        app_settings: the application settings (will be used to determine the conversation path)
        logger: the logger to use and add to the ChatContext
    """
    conversation_path = app_settings.conversation_path / conversation_id

    try:
        with open(conversation_path / "conversation.json", "r") as f:
            conv_dict = json.loads(f.read())
            id = conv_dict["conversation_id"]

        return ChatContext(
            **conv_dict,
            key_storage_backend=load_key_storage_backend(
                app_settings=app_settings, conversation_id=id
            ),
            file_storage_backend=load_file_storage_backend(
                app_settings=app_settings, conversation_id=id
            ),
            default_logger=logger,
            settings=app_settings,
        )

    except Exception as e:
        raise ConversationNotReadableException(
            f"Couldn't load conversation due to `{str(e)}`"
        )
