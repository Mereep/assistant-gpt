from exceptions.repository_exceptions import RepositoryException
from repository.file_filestorage_backend import FileFileStorageBackend
from repository.i_file_storage_backend import IFileStorageBackend
from repository.i_key_storage_backend import IKeyStorageBackend
from utils.app_settings import AppSettings


def load_key_storage_backend(
    app_settings: AppSettings, conversation_id: str
) -> IKeyStorageBackend:
    """Loads the key storage backend for files from the application settings
    Args:
        app_settings: the application settings
        conversation_id: the id of the conversation
    """
    if app_settings.key_storage_backend == "file":
        from repository.file_key_storage_backend import FileKeyKeyStorageKeyBackend

        return FileKeyKeyStorageKeyBackend(
            app_settings.conversation_file_index_storage / conversation_id
        )
    else:
        raise RepositoryException(
            f"Unknown key storage backend `{app_settings.key_storage_backend}`"
        )


def load_file_storage_backend(
    app_settings: AppSettings, conversation_id: str
) -> IFileStorageBackend:
    """Loads the storage backend from the application settings
    Args:
        app_settings: the application settings
        conversation_id: the id of the conversation
    """
    if app_settings.file_storage_backend == "file":
        return FileFileStorageBackend(
            app_settings.conversation_filesystem_path / conversation_id
        )
    else:
        raise RepositoryException(
            f"Unknown file storage backend `{app_settings.file_storage_backend}`"
        )
