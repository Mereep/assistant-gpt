import requests

from datatypes.chat_context import ChatContext
from datatypes.command_argument import CommandArgument
from exceptions.commands_execption import CommandExecutionError
from gpt_commands.i_command import ICommand

from utils.multimedia import try_extract_text


class ReadWebsiteCommand(ICommand):

    @classmethod
    def name(cls) -> str:
        return 'read_website'

    @classmethod
    def description(cls) -> str:
        return f'Reads the content of a website (http:// or https://) and returns the information. ' \
               f'Always use this command if you ' \
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
            downloaded = requests.get(url, timeout=5, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/111.0'
            }).content
            if not downloaded:
                return f"Could not read the website `{url}`. This is likely a permanent error."

            extract = try_extract_text(data=downloaded, ctx=chat_context)
            if extract:
                extract = extract.strip()

                # make it shorter if it is too long
                max_len = int(chat_context.settings.max_token_len_history // 1.5 * 4)
                if len(extract) > max_len:
                    # get the start and end of the document (this remains abstract and summary more likey)
                    halfes = max_len // 2
                    extract = extract[:halfes] + '...' + extract[-halfes:]
                return f'----BEGIN WEBSITE `{url}`----\n' + extract + f'\n----END WEBSITE `{url}`----\n'
            else:
                return f"The website`{url}` has no content,"
        except Exception as e:
            raise CommandExecutionError(
                reason_for_bot=f"Error reading website due to `{e}`",
                actual_reason=f"Error reading website due to `{e}`"
            )

    @classmethod
    def needs_confirmation(cls) -> bool:
        return True
