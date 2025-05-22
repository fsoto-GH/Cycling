from dataclasses import dataclass
from datetime import timedelta


@dataclass
class RestStop:
    name: str
    hours: dict[int: str]
    address: str


@dataclass
class Split:
    distance: float
    rest_stop: RestStop | None = None
    # fields below override base calculations
    moving_speed: float | None = None
    down_time: timedelta | None = None
    sleep_time: timedelta | None = None



