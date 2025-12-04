from dataclasses import dataclass
from datetime import datetime, timedelta

from Cycling.pace_calculator.SplitDetail import SplitDetail


@dataclass
class SegmentDetail:
    split_details: list[SplitDetail]
    start_time: datetime
    end_time: datetime
    total_elapsed_time: timedelta
    total_moving_time: timedelta
    total_down_time: timedelta
    total_sleep_time: timedelta
    total_adjustment_time: timedelta
