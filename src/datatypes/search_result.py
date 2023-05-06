import dataclasses


@dataclasses.dataclass(frozen=True)
class SearchResult:
    url: str
    title: str
    description: str

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(self.url)
