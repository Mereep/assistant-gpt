from datatypes.chat_context import ChatContext
from datatypes.command_argument import CommandArgument
from exceptions.commands_execption import CommandExecutionError
from gpt_commands.i_command import ICommand
import trafilatura


class ReadWebsiteCommand(ICommand):

    @classmethod
    def name(cls) -> str:
        return 'read_website'

    @classmethod
    def description(cls) -> str:
        return f'Reads the content of a website (http:// or https://) and returns the information. ' \
               f'Always use this command if your' \
               f'are asked for specific information on a web page.'

    @classmethod
    def arguments(cls) -> list[CommandArgument]:
        return [CommandArgument(name='url',
                                type=str,
                                help='the url to fetch the website from',
                                required=True,
                                )]

    def execute(self, chat_context: ChatContext, **args) -> str:
        url = args.pop('url')

        try:
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return f"Could not read the website `{url}`. This is likely a permanent error."
            extract = trafilatura.extract(downloaded).strip()
            return f'----BEGIN WEBSITE `{url}`---- \n' + (extract or "no content") + f'\n----END WEBSITE `{url}` ---- \n'
        except Exception as e:
            raise CommandExecutionError(
                reason_for_bot=f"Error reading website due to `{e}`",
                actual_reason=f"Error reading website due to `{e}`"
            )

    @classmethod
    def needs_confirmation(cls) -> bool:
        return True
