from __future__ import annotations

import datetime

import requests

from datatypes.chat_context import ChatContext
from datatypes.command_argument import CommandArgument
from datatypes.news_article import TNewsArticles, NewsArticle
from exceptions.commands_execption import CommandExecutionError
from gpt_commands.i_command import ICommand


class NewsApiCommand(ICommand):
    @classmethod
    def name(cls) -> str:
        return "news_api"

    @classmethod
    def description(cls) -> str:
        return f"Provides news articles using the NewsAPI service."

    @classmethod
    def arguments(cls) -> list[CommandArgument]:
        return [
            CommandArgument(
                name="query", type=str, help="the query to search for", required=True
            ),
            CommandArgument(
                name="page",
                type=int,
                help="The page to return defaults to 1 if not given.",
                required=False,
            ),
            CommandArgument(
                name="language",
                type=str,
                help="limit the search to a specific language like "
                '(en, de, fr, ...). Defaults to "en".',
                required=False,
            ),
        ]

    def execute(self, chat_context: ChatContext, **args) -> str:
        query = args.pop("query")
        page = args.pop("page", 1)
        language = args.pop("language", "en")
        if page < 1:
            page = 1

        try:
            news_articles = fetch_news(
                query,
                language=language,
                api_key=chat_context.settings.newsapi_key,
                page=page,
            )
        except Exception as e:
            raise CommandExecutionError(
                reason_for_bot="Error fetching news articles: {}".format(e),
                actual_reason="Error fetching news articles: {}".format(e),
            )
        if len(news_articles) == 0:
            return f"No news articles found for query `{query}` using {self.name()}."

        article_str = ""
        article: NewsArticle
        for article in news_articles:
            article_str += (
                f"- {article.published_at.strftime('%Y-%m-%d')}: "
                f"Tile: `{article.title}` "
                f"(Source: `{article.source}`)\n"
                f"Description: `{article.summary}`\n"
                f"URL: `{article.url}`\n"
            )

        return article_str

    @classmethod
    def needs_confirmation(cls) -> bool:
        return True


def fetch_news(
    query: str,
    api_key: str,
    page: int = 1,
    page_size: int = 15,
    language: str = "en",
) -> TNewsArticles:
    """
    Queries the NewsAPI for news articles.

    :param query: The query to search for
    :param api_key: The API key to use
    :param page: The page to return defaults to 1 if not given.
    :param page_size: The number of articles to return per page. Defaults to 15.
    :param language: limit the search to a specific language like (en, de, fr, ...)
    :return: A list of NewsArticle instances
    :raises Exception: If the request fails
    """
    # Set up the endpoint and parameters
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "sortBy": "publishedAt",
        "apiKey": api_key,
        "language": language,
        "pageSize": page_size,
        "page": page,
    }

    # Send the request and parse the response
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        articles = data["articles"]

        # Transform articles into NewsArticle dataclass instances
        news_articles = [
            NewsArticle(
                title=article["title"],
                source=article["source"]["name"],
                published_at=datetime.datetime.fromisoformat(
                    article["publishedAt"][:-1]
                ),
                url=article["url"],
                summary=article["description"],
            )
            for article in articles
        ]

        return TNewsArticles(news_articles)
    else:
        raise Exception(
            f"Couldn't fetch news data due to: {response.status_code} {response.text}"
        )
