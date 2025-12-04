from dataclasses import dataclass
from datetime import datetime, timedelta

from Cycling.pace_calculator.Split import Split
from Cycling.pace_calculator.SplitDetail import SubSplitDetail


@dataclass
class SubSplitCalculator:

    @staticmethod
    def get_sub_split_details(split: Split,
                              start_distance: float,
                              start_time: datetime,
                              down_time: timedelta,
                              moving_speed: float):
        pass


@dataclass
class SubSplitCalculatorV1(SubSplitCalculator):
    @staticmethod
    def get_sub_split_details(split: Split,
                              start_distance: float,
                              start_time: datetime,
                              down_time: timedelta,
                              moving_speed: float):
        sub_split_distances = split.sub_split_distances
        res: list[SubSplitDetail] = []

        # avoid technical computations and evenly split down_time
        # could consider this being = moving_time * split.down_time_ratio or segment.down_time_ratio
        # however, we'd need to handle cases where down_time is explicitly defined for splits
        sub_split_down_time = down_time / len(sub_split_distances)

        for sub_split_distance in sub_split_distances:
            sub_split_moving_time = timedelta(hours=sub_split_distance / moving_speed)
            sub_split_total_time = sub_split_moving_time + sub_split_down_time

            sub_split_detail = SubSplitDetail(
                distance=sub_split_distance,
                start_time=start_time,
                end_time=start_time + sub_split_total_time,
                moving_speed=moving_speed,
                moving_time=sub_split_moving_time,
                down_time=sub_split_down_time,
                split_time=sub_split_total_time,
                total_time=sub_split_total_time,  # equal to split time because sub-splits do not consider adjusted time
                pace=sub_split_distance / (sub_split_total_time.total_seconds() / 3600),
                start_distance=start_distance
            )

            start_time += sub_split_moving_time + sub_split_down_time
            start_distance += sub_split_distance

            res.append(sub_split_detail)
        return res
