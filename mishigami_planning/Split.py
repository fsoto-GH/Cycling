import datetime
from dataclasses import dataclass
from datetime import timedelta, datetime

from Cycling.mishigami_planning.RestStop import RestStop


@dataclass
class Split:
    distance: float
    start_mile: float = 0  # consider implementing this in the case there is a gap between splits
    # this overrides any distance sub_split distances
    sub_split_count: int | None = None
    sub_split_distance: float | None = None
    rest_stop: RestStop | None = None
    # fields below override base calculations
    moving_speed: float | None = None
    down_time: timedelta | None = None
    adjustment_time: timedelta | None = None


@dataclass
class SubSplit:
    total_distance: float
    down_time_ratio: float
    moving_speed: float
    start_time: datetime
    start_offset: float
    sub_split_distances: float


@dataclass
class SubSplitDetail:
    distance: float
    span: str
    moving_speed: float
    adjustment_hours: timedelta  # maybe int???
    moving_time: float
    split_time: float
    down_time: float
    total_time: float
    pace: float
    start_time: datetime
    adjustment_start: datetime
    end_time: datetime


@dataclass
class SplitDetail:
    distance: float
    span: str
    moving_speed: float
    adjustment_time: timedelta
    moving_time: timedelta
    split_time: timedelta
    split_speed: float
    down_time: timedelta
    total_time: timedelta
    pace: float
    start_time: datetime
    adjustment_start: Optional[datetime]
    stop: Optional[Any]
    end_time: datetime

    sub_splits: list[SubSplitDetail]