from __future__ import annotations

import logging

_BASE_LOGGER: logging.Logger | None = None


def get_base_logger() -> logging.Logger:
    global _BASE_LOGGER
    if _BASE_LOGGER is None:
        _BASE_LOGGER = logging.getLogger("base_logger")
        _BASE_LOGGER.setLevel(logging.DEBUG)
        _BASE_LOGGER.formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        _BASE_LOGGER.addHandler(logging.StreamHandler())
        _BASE_LOGGER.setLevel(logging.DEBUG)

    return _BASE_LOGGER
