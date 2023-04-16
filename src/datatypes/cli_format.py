from __future__ import annotations

import dataclasses

from rich.style import Style


@dataclasses.dataclass
class CliFormat:
    style: Style | None = None
    delay: float = 0.
    new_line: bool = True

