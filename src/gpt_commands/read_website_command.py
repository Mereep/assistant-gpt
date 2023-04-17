import requests

from datatypes.chat_context import ChatContext
from datatypes.command_argument import CommandArgument
from exceptions.commands_execption import CommandExecutionError
from gpt_commands.i_command import ICommand

from utils.multimedia import try_extract_text

PAGE_CACHE: dict[str, str] = {}


class ReadWebsiteCommand(ICommand):

    @classmethod
    def name(cls) -> str:
        return 'read_website'

    @classmethod
    def description(cls) -> str:
        return f'Reads the content of a website and returns the information or other fetchable documents. ' \
               f'Always use this command if you ' \
               f'are asked for specific information on a web page or pdf document.' \
               f'If the document is big it is split into multiple parts. You will be informed if this happens.'

    @classmethod
    def arguments(cls) -> list[CommandArgument]:
        return [CommandArgument(name='url',
                                type=str,
                                help='The url to fetch the website from.',
                                required=True),
                CommandArgument(name='page',
                                type=int,
                                help='the page you want to read. Default is 1.',
                                required=False)
                                ]

    def execute(self, chat_context: ChatContext, **args) -> str:
        url = args.pop('url')
        page = args.pop('page', 1)
        global PAGE_CACHE

        try:
            if url in PAGE_CACHE:
                downloaded = requests.get(url, timeout=5, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/111.0'
                }).content
            else:
                downloaded = PAGE_CACHE[url]

            if not downloaded:
                return f"Could not read the website `{url}`. This is likely a permanent error."

            extract = try_extract_text(data=downloaded, ctx=chat_context)
            if extract:
                extract = extract.strip()
                PAGE_CACHE[url] = extract

                # make it shorter if it is too long
                max_len = int(chat_context.settings.max_token_len_history // 1.5 * 4)
                n_pages = 1
                if len(extract) > max_len:
                    # get the start and end of the document (this remains abstract and summary more likey)
                    part = extract[(page - 1) * max_len:page * max_len]
                    n_pages = len(extract) // max_len + 1
                res = f'----BEGIN WEBSITE `{url}` page #{page} of {n_pages}----\n' + extract + f'\n----END WEBSITE `{url}` page #{page} of {n_pages} ----\n'
                if n_pages > 1:
                    res += f'If you want to read the next page, please use the command with page set to{page + 1}`.'
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
