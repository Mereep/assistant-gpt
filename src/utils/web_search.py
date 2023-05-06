import re
from typing import Iterable

import requests
from bs4 import BeautifulSoup
from googlesearch import search, SearchResult as GoogleSearchResult

from datatypes.chat_context import ChatContext
from datatypes.search_result import SearchResult


def do_google_search(q: str, lang: str, ctx: ChatContext) -> list[SearchResult]:
    try:
        results: list[GoogleSearchResult] = \
            search(
                q,
                num_results=ctx.num_search_results,
                lang=lang,
                advanced=True,

        )
        ret = []
        for res in results:
            ret.append(SearchResult(url=res.url, title=res.title, description=res.description))

        return ret
    except Exception as e:
        ctx.default_logger.warning("Error while searching "
                                   "{!s}: ".format(e))
        return []


def do_bing_search(q: str, lang: str, ctx: ChatContext, first: int = 0) -> list[SearchResult]:
    try:
        url = f'https://www.bing.com/search?q={q}&first={first}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/89.0.4389.82 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            ctx.default_logger.warning("Error while searching Bing"
                                       "{!s}: ".format(response.status_code))
            return []

        search_results = []
        contents = response.content
        soup = BeautifulSoup(contents, "html.parser")
        did_error = False
        for res in soup.find_all(name='li',
                                 attrs={'class': re.compile('.*b_algo.*')},
                                 recursive=True):
            try:
                a = res.find(name='h2').find(name='a')
                title = a.text
                link = a['href']
                content = res.find('div', attrs={'class': 'b_caption'}).text
                search_results.append(SearchResult(url=link, title=title, description=content))
            except Exception as e:
                ctx.default_logger.warning("Error while searching bing {e!s}. Ignoring trying more...".format(e=e))
                did_error = True

        # filter doubled results
        search_results = list(set(search_results))
        if first + len(search_results) < ctx.num_search_results:
            if not did_error:  # if we did error we do *not* want to try again as we would endlessly loop
                ctx.default_logger.debug("Not enough Bing results, trying more...")
                search_results.extend(do_bing_search(q, lang, ctx, first=first + len(search_results) + 1))

        return search_results

    except Exception as e:
        ctx.default_logger.warning("Error while searching "
                                   "{!s}: ".format(e))
        return []


def do_yahoo_search(q: str, lang: str, ctx: ChatContext) -> list[SearchResult]:
    raise NotImplementedError('Yahoo hides the links in the search results, '
                              'we would need a headless browser to fetch them. Code below fetches the `broken` links ')
    try:
        url = f'https://search.yahoo.com/search?p={q}&n={ctx.num_search_results}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/89.0.4389.82 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        search_results = []
        contents = response.content
        soup = BeautifulSoup(contents, "html.parser")
        for res in soup.find_all(name='div',
                                 attrs={'class': re.compile('.*dd algo algo-sr*')},
                                 recursive=True):
            a, = [*res.find_all(name='a', attrs={'class': re.compile('.*d-ib.*')})]
            link = a['href']
            title = a['aria-label']
            summary = res.find(name='div', attrs={'class': re.compile('.*compText aAbs.*')}).text
            search_results.append(SearchResult(url=link, title=title, description=summary))

    except Exception as e:
        ctx.default_logger.warning('Error while searching yahoo '
                                   '{!s} (Code: 982039482) '.format(e))
        return []

    return search_results
