from dataclasses import dataclass
from datetime import datetime, timedelta

from Cycling.pace_calculator.CourseDetail import CourseDetail
from Cycling.pace_calculator.SegmentDetail import SegmentDetail
from Cycling.pace_calculator.DetailLines import KOMDetailLine, KOMOptionalDetailLine
from Cycling.pace_calculator.Segment import Segment
from Cycling.pace_calculator.Split import Split
from Cycling.pace_calculator.SplitDetail import SplitDetail
from Cycling.pace_calculator.SubSplitCalculator import SubSplitCalculatorV1
from Cycling.pace_calculator.SubSplitMode import EvenSubSplitMode, FixedDistanceSubSplitMode


@dataclass
class Course:
    segments: list[Segment]
    KOMs: list[KOMDetailLine | KOMOptionalDetailLine]  # TODO: Implement KOM, this might be a Printer object detail tbh
    init_moving_speed: float
    min_moving_speed: float
    down_time_ratio: float = 0
    split_decay: float = 0
    start_time: datetime | None = datetime.today()

    def compute_course_details(self) -> CourseDetail:
        """
        Computes the detailed breakdown of the course based on segments and splits.

        :return: A CourseDetail object containing detailed information about the course.
        """
        curr_start_time: datetime = self.start_time
        curr_moving_speed: float = self.init_moving_speed
        curr_distance: float = 0
        segment_details: list[SegmentDetail] = []

        # totals
        total_moving_time: timedelta = timedelta(hours=0)
        total_down_time: timedelta = timedelta(hours=0)
        total_sleep_time: timedelta = timedelta(hours=0)

        for segment in self.segments:
            # check if segment has moving speed defined, as it overrides the decayed/computed moving speed
            # this can account/simulate for 'recovered'/'fatigued' legs
            if segment.moving_speed is not None:
                curr_moving_speed = segment.moving_speed

            split_details: list[SplitDetail] = []
            for i, split in enumerate(segment.splits):
                # check if split has moving speed defined,
                # as it overrides the decayed/computed moving speed AND segment moving speed
                if split.moving_speed is not None:
                    curr_moving_speed = split.moving_speed

                moving_time = timedelta(hours=split.distance / curr_moving_speed)

                down_time: timedelta = moving_time * self.down_time_ratio
                # if a segment has defined down_time, it overrides the course-computed down_time
                if segment.down_time_ratio is not None:
                    down_time: timedelta = moving_time * segment.down_time_ratio
                # if a split has defined down_time, it overrides the course and segment-computed down_time
                if split.down_time is not None:
                    down_time = split.down_time
                # check if this is the last split of the segment and no_end_downtime is set
                if i == len(segment.splits) - 1 and segment.no_end_down_time:
                    down_time = timedelta(hours=0)

                split_time = moving_time + down_time
                total_time = split_time + split.adjusted_time
                sub_split_details = SubSplitCalculatorV1.get_sub_split_details(
                    split=split,
                    start_distance=curr_distance,
                    start_time=curr_start_time,
                    down_time=down_time,
                    moving_speed=curr_moving_speed
                )

                split_detail = SplitDetail(
                    distance=split.distance,
                    start_time=curr_start_time,
                    end_time=curr_start_time + total_time,
                    adjustment_start=curr_start_time + split_time,
                    moving_speed=curr_moving_speed,
                    moving_time=moving_time,
                    down_time=down_time,
                    adjustment_time=split.adjusted_time,
                    split_time=split_time,
                    total_time=total_time,
                    pace=split.distance / (total_time.total_seconds() / 3600),
                    start_distance=curr_distance,
                    rest_stop=split.rest_stop,
                    sub_splits=sub_split_details
                )

                # NOTE: The operations below are for post-split calculation updates.
                # Shifting start time, updating subsequent moving speed, etc.

                # decay split moving speed for next split, limit to min_moving_speed
                next_decayed_moving_speed = curr_moving_speed - self.split_decay

                min_moving_speed = self.min_moving_speed
                # override with segment min_moving_speed if defined
                # this can account/simulate for stronger/weaker/non-uniform efforts (climb, descent, etc)
                if segment.min_moving_speed is not None:
                    min_moving_speed = segment.min_moving_speed

                curr_moving_speed = max(next_decayed_moving_speed, min_moving_speed)
                curr_distance += split.distance
                curr_start_time += total_time

                split_details.append(split_detail)
            segment_details.append(SegmentDetail(split_details=split_details))

            # account for sleep time between segments
            total_moving_time += sum((x.moving_time for x in split_details), timedelta(0))
            total_down_time += sum((x.down_time for x in split_details), timedelta(0))
            total_sleep_time += segment.sleep_time

            curr_start_time += segment.sleep_time

        return CourseDetail(
            segment_details=segment_details,
            start_time=self.start_time,
            end_time=curr_start_time,
            total_elapsed_time=curr_start_time - self.start_time,
            total_moving_time=total_moving_time,
            total_down_time=total_down_time,
            total_sleep_time=total_sleep_time
        )
