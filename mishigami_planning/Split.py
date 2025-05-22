from dataclasses import dataclass
from datetime import timedelta

from mishigami_planning.RestStop import RestStop


@dataclass
class Split:
    distance: float
    # this overrides any distance sub_split distances
    sub_split_count: int | None = None
    rest_stop: RestStop | None = None
    # fields below override base calculations
    moving_speed: float | None = None
    down_time: timedelta | None = None
    adjustment_time: timedelta | None = None
