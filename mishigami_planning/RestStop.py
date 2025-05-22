from dataclasses import dataclass


@dataclass
class RestStop:
    name: str
    hours: dict[int: str]
    address: str
    alt: str | None = None
