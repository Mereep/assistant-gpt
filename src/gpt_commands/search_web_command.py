import datetime
import random

from googlesearch import search, SearchResult

from datatypes.chat_context import ChatContext
from datatypes.command_argument import CommandArgument
from exceptions.commands_execption import CommandExecutionError
from gpt_commands.i_command import ICommand
import gettext

from utils import web_search

_ = gettext.gettext


class SearchWebCommand(ICommand):
    @classmethod
    def name(cls) -> str:
        return "search_web"

    @classmethod
    def description(cls) -> str:
        return (
            "Search the web using a websearch provider. Will return the first search results, "
            "a link and a short description. "
        )

    @classmethod
    def arguments(cls) -> list[CommandArgument]:
        return [
            CommandArgument(
                name="search_query", type=str, required=True, help="search query"
            ),
            CommandArgument(
                name="language",
                type=str,
                required=False,
                help='language to search (e.g. "de" for German, '
                '"en" for English, "fr" for French, etc. Default: "en")',
            ),
        ]

    def execute(self, chat_context: ChatContext, **args) -> str:
        default_lang = "en"
        q = args.pop("search_query")
        lang = args.pop("language", default_lang)

        # check if the search has been conducted recently and
        # @TODO make that configurable (by time or by amount of messages passed since the query or both)
        for index, message in chat_context.filter_chat_gpt_commands(
            command_name=self.name()
        ):
            if message.arguments["search_query"].lower().strip() == q.lower().strip():
                old_lang = (
                    message.arguments["language"]
                    if "language" in message.arguments
                    else default_lang
                )
                old_lang = old_lang.strip().lower()
                if old_lang == lang:
                    if message.created_ts > (
                        datetime.datetime.now().timestamp() - 60 * 60
                    ):
                        return (
                            f"Your searched this already for query `{q}` and lang `{lang}` "
                            f"in message with the index number #{index} recently. "
                            f"The results are likely be found in the response message at index #{index+1}. "
                            f"Please use the information in our conversation history before searching again."
                        )

        try:
            res = []
            for provider in chat_context.allowed_search_providers:
                if provider == 'google':
                    res.extend(web_search.do_google_search(q=q, lang=lang, ctx=chat_context))
                elif provider == 'yahoo':
                    res.extend(web_search.do_yahoo_search(q=q, lang=lang, ctx=chat_context))
                elif provider == 'bing':
                    res.extend(web_search.do_bing_search(q=q, lang=lang, ctx=chat_context))

                if len(res) >= chat_context.num_search_results:
                    break

            if len(res) == 0:
                return "No results found for search query `{q}`.".format(q=q)
            else:
                out = "--- BEGIN SEARCH RESULTS ---\n"
                for i, r in enumerate(res):
                    out += f"- Result #{i+1}: {r.url}: ({r.description})\n"
                out += "--- END SEARCH RESULTS ---"

                return out
        except Exception as err:
            raise CommandExecutionError(
                reason_for_bot=f"Sorry, I can't search the web at the moment.",
                actual_reason=f"Couldn't search the web due to unknown error {err}",
            )

    @classmethod
    def needs_confirmation(cls) -> bool:
        return True
