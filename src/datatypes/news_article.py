from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import NewType


@dataclass
class NewsArticle:
    title: str
    source: str
    published_at: datetime.datetime
    url: str
    summary: str | None = None


TNewsArticles = NewType("NewsArticles", list[NewsArticle])
