from dataclasses import dataclass
@dataclass
class PageContent:
    url: str
    title: str
    text: str

@dataclass
class ContextEntry:
    id: int
    title: str
    fragments: list[str]