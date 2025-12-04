from datetime import timedelta, datetime

from Cycling.pace_calculator.Course import Course
from Cycling.pace_calculator.CourseDetailPrinter import CourseDetailPrinter
from Cycling.pace_calculator.RestStop import RestStop, WeeklyOpenHours, FixedOpenHours
from Cycling.pace_calculator.Segment import Segment
from Cycling.pace_calculator.Split import Split
from Cycling.pace_calculator.SubSplitMode import FixedDistanceSubSplitMode


def main():
    course = Course(
        segments=[
            Segment(
                splits=[
                    Split(
                        distance=100,
                        sub_split_mode=FixedDistanceSubSplitMode(
                            sub_split_distance=50
                        ),
                        rest_stop=RestStop(
                            name="McDonald's",
                            open_hours=WeeklyOpenHours(
                                mon="6:00a -  9:00p",
                                tue="9:00a - 10:00p",
                            ),
                            address="7832 S Western Ave, Chicago, IL 60620",
                            alt="https://share.google/JGoFaIMStVTrwLUBB",
                        )
                    ),
                    Split(
                        distance=100,
                        sub_split_mode=FixedDistanceSubSplitMode(
                            sub_split_distance=50
                        ),
                        rest_stop=RestStop(
                            name="McDonald's",
                            open_hours=FixedOpenHours(
                                hours="24hrs",
                            ),
                            address="7832 S Western Ave, Chicago, IL 60620",
                            alt="https://share.google/JGoFaIMStVTrwLUBB",
                        ),
                        moving_speed=12,  # perhaps a climb here, so slower speed
                    ),
                ],
                sleep_time=timedelta(hours=11),
                no_end_down_time=False  # for whatever reason, we want down_time after last split
            ),
            Segment(
                splits=[
                    Split(
                        distance=300,
                        sub_split_mode=FixedDistanceSubSplitMode(
                            sub_split_distance=50
                        ),
                        rest_stop=RestStop(
                            name="McDonald's",
                            open_hours=WeeklyOpenHours(
                                mon="6:00a -  9:00p",
                                tue="9:00a - 10:00p"
                            ),
                            address="7832 S Western Ave, Chicago, IL 60620",
                            alt="https://share.google/JGoFaIMStVTrwLUBB",
                        ),
                        moving_speed=18,  # going a little faster the second 'day'
                        down_time=timedelta(minutes=5),  # brief rest stop
                    ),
                    Split(
                        distance=50,
                        sub_split_mode=FixedDistanceSubSplitMode(
                            sub_split_distance=50
                        ),
                        rest_stop=RestStop(
                            name="McDonald's",
                            open_hours=FixedOpenHours(
                                hours="24hrs",
                            ),
                            address="7832 S Western Ave, Chicago, IL 60620",
                            alt="https://share.google/JGoFaIMStVTrwLUBB",
                        ),
                    ),
                ],
                # notice how sleep_time is not defined here, so it will default to 0
            )
        ],
        KOMs=[],
        start_time=datetime(2025, 12, 13, 8, 0, 0),
        init_moving_speed=17,
        min_moving_speed=15,
        down_time_ratio=0.05,
        split_decay=0.1
    )

    course_details = course.compute_course_details()

    printer = CourseDetailPrinter(
        course_details=course_details
    )

    printer.print()


if __name__ == '__main__':
    main()
