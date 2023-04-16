import typing

from .ask_human_command import AskHumanCommand
from .i_command import ICommand
from .storage_read_command import StorageReadCommand
from .storage_write_command import StorageWriteCommand
from .storage_delete_command import StorageDeleteCommand
from .answer_command import AnswerCommand
from .read_file_command import ReadFileCommand
from .write_file_command import WriteFileCommand
from .list_files_command import ListFilesCommand
from .date_command import DateCommand
from .news_api import NewsApiCommand
from .read_website_command import ReadWebsiteCommand
from .search_web_command import SearchWebCommand
from .ask_ai_agent_command import AskAiAgentCommand


""" Available commands to be used by the LLM bot. """
GPT_COMMANDS: dict[str, typing.Type[ICommand]] = {
    AskHumanCommand.name(): AskHumanCommand,
    StorageReadCommand.name(): StorageReadCommand,
    StorageWriteCommand.name(): StorageWriteCommand,
    StorageDeleteCommand.name(): StorageDeleteCommand,
    AnswerCommand.name(): AnswerCommand,
    ReadFileCommand.name(): ReadFileCommand,
    WriteFileCommand.name(): WriteFileCommand,
    ListFilesCommand.name(): ListFilesCommand,
    DateCommand.name(): DateCommand,
    NewsApiCommand.name(): NewsApiCommand,
    ReadWebsiteCommand.name(): ReadWebsiteCommand,
    SearchWebCommand.name(): SearchWebCommand,
    AskAiAgentCommand.name(): AskAiAgentCommand,
}
