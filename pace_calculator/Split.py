from dataclasses import dataclass
from datetime import timedelta

from Cycling.pace_calculator.RestStop import RestStop
from Cycling.pace_calculator.SubSplitMode import EvenSubSplitMode, FixedDistanceSubSplitMode, CustomSubSplitMode


@dataclass
class Split:
    distance: float
    sub_split_mode: EvenSubSplitMode | FixedDistanceSubSplitMode | CustomSubSplitMode
    rest_stop: RestStop | None = None
    # this field overrides any down_time computed at segment level
    down_time: timedelta | None = None
    # this field overrides any moving speed set at parent levels (segment or course)
    moving_speed: float | None = None
    adjusted_time: timedelta = timedelta(hours=0)

    @property
    def sub_split_distances(self):
        return self.sub_split_mode.sub_splits(self.distance)
