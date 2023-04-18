from pathlib import Path
from typing import Literal

import yaml

from exceptions.settings_exception import SettingsNotReadableException


class AppSettings:
    yaml: dict
    config_file: Path

    @property
    def gpt_api_key(self) -> str:
        return self.yaml["credentials"]["chatgpt_api_key"]

    @property
    def newsapi_key(self) -> str:
        return self.yaml["credentials"]["newsapi_key"]

    @property
    def user_input_prompt_method(self) -> Literal["cli"]:
        return self.yaml["general"]["query_user_method"]

    @property
    def allowed_commands(self) -> list[str]:
        return [
            str(command).strip() for command in self.yaml["general"]["allowed_commands"]
        ]

    @property
    def max_response_repairment_attempts(self) -> int:
        return int(self.yaml["general"]["max_response_repairment_attempts"])

    @property
    def conversation_path(self) -> Path:
        return Path("..") / "data" / "conversations"

    @property
    def conversation_file_index_storage(self) -> Path:
        return Path("..") / "data" / "file_index_storage"

    @property
    def conversation_filesystem_path(self) -> Path:
        return Path("..") / "data" / "conversation_filesystem"

    @property
    def key_storage_backend(self) -> Literal["file"]:
        return self.yaml["general"]["key_storage_backend"]

    @property
    def file_storage_backend(self) -> Literal["file"]:
        return self.yaml["general"]["file_storage_backend"]

    @property
    def model(self) -> str:
        return self.yaml["general"]["model"]

    @property
    def log_level(self) -> str:
        return self.yaml["general"]["log_level"]

    @property
    def max_token_len_history(self) -> int:
        return self.yaml["prompt"]["max_token_len_history"]

    @property
    def ai_default_role(self) -> str:
        return self.yaml["prompt"]["ai_default_role"]

    @property
    def default_ai_tasks(self) -> list[str]:
        return list(self.yaml["prompt"]["default_ai_tasks"])

    @property
    def own_names(self) -> list[str]:
        return list(self.yaml["general"]["own_names"])

    def __init__(self, config_file: Path):
        self.config_file = config_file
        self.load_settings()

    def load_settings(self):
        # write the yaml as json to yaml_document var
        try:
            with open(self.config_file, "r") as file:
                self.yaml = yaml.safe_load(file)
        except Exception as e:
            raise SettingsNotReadableException(
                f"Couldn't parse settings file `{file!s}` " f"due to `{str(e)}`"
            )
