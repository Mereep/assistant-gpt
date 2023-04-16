from googlesearch import search, SearchResult

from datatypes.chat_context import ChatContext
from datatypes.command_argument import CommandArgument
from exceptions.commands_execption import CommandExecutionError
from gpt_commands.i_command import ICommand
import gettext

_ = gettext.gettext


class SearchWebCommand(ICommand):
    @classmethod
    def name(cls) -> str:
        return 'search_web'

    @classmethod
    def description(cls) -> str:
        return 'Search the web using Google. Will return the first search results, a link and a short description.'

    @classmethod
    def arguments(cls) -> list[CommandArgument]:
        return [CommandArgument(name='search_query',
                                type=str,
                                required=True,
                                help='search query'),
                CommandArgument(name='language',
                                type=str,
                                required=False,
                                help='language to search (e.g. "de" for German, '
                                     '"en" for English, "fr" for French, etc. Default: "en")'),

                ]

    def execute(self, chat_context: ChatContext, **args) -> str:
        q = args.pop('search_query')
        lang = args.pop('language', 'en')
        try:
            res: list[SearchResult] = list(search(q, num_results=10, lang=lang, advanced=True, ))
            if len(res) == 0:
                return "No results found for search query `{q}`.".format(q=q)
            else:
                out = '--- BEGIN SEARCH RESULTS ---\n'
                for i, r in enumerate(res):
                    out += f"- Result: {i}: {r.url}: ({r.description})\n"
                out += '--- END SEARCH RESULTS ---'

                return out
        except Exception as err:
            raise CommandExecutionError(
                reason_for_bot=f"Sorry, I can't search the web at the moment.",
                actual_reason=f"Couldn't search the web due to unknown error {err}")

    @classmethod
    def needs_confirmation(cls) -> bool:
        return True
