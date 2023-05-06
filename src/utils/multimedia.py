from __future__ import annotations

from io import StringIO, BytesIO

import trafilatura
from pypdf import PdfReader

from datatypes.chat_context import ChatContext


def try_extract_text(data: bytes, ctx: ChatContext) -> str | None:
    """
    Tries to extract the text from the data
    (will try html, pdf and such)
    :param data:
    :param ctx:
    :return:
    """
    try:
        res = try_extract_from_html(data=data, ctx=ctx)
        if res:
            return res
    except Exception as e:
        ctx.default_logger.debug("Error while extracting text from html: " + str(e))
        pass

    try:
        res = try_extract_from_pdf(data=data, ctx=ctx)
        if res:
            return res
    except Exception as e:
        ctx.default_logger.debug("Error while extracting text from pdf: " + str(e))

    return None


def try_extract_from_html(data: bytes, ctx: ChatContext) -> str | None:
    return trafilatura.extract(data.decode("utf-8"))


def try_extract_from_pdf(data: bytes, ctx: ChatContext) -> str | None:
    # creating a pdf reader object
    data = BytesIO(data)
    reader = PdfReader(data)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    return text
