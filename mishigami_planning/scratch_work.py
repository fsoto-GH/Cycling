from Cycling.mishigami_planning.SubDistancePaceCalculator import SubDistancePaceCalculator
from Cycling.mishigami_planning.Utils import splits_from_distances
from datetime import datetime

from PaceCalculatorPrinter import PaceCalculatorPrinter
from Split import Split


def main():
    distance = 379.6
    split_count = 5
    miles_to_start: float = 0

    markers = [miles_to_start + x for x in [42.5, 78.6, 124.6]]

    if miles_to_start != 0:
        markers = [miles_to_start] + markers

    split_distances = splits_from_distances(markers)

    # if splits are not defined, generate based on distance and split
    if split_distances is None or len(split_distances) == 0:
        split_distances = [distance / split_count] * split_count

    start_moving_speed = 17.5
    min_moving_speed = 15
    decay_per_split = 0.05
    downtime_ratio = 0.05
    sub_split_distances = 10
    with_sub_splits = False
    start_offset = 0

    start_time = datetime(year=2025, month=10, day=3, hour=8, minute=0)
    no_end_downtime = True

    splits = [Split(distance=split_distance) for split_distance in split_distances]

    pace_calc = SubDistancePaceCalculator()

    # pace detail is good if you intend to sleep after a split
    pace_calc.set_split_info(splits=splits,
                             downtime_ratio=downtime_ratio,
                             start_time=start_time,
                             no_end_downtime=no_end_downtime,
                             start_offset=start_offset,
                             start_moving_speed=start_moving_speed,
                             min_moving_speed=min_moving_speed,
                             decay_per_split=decay_per_split,
                             sub_split_distances=sub_split_distances)

    pace_calculator_printer = PaceCalculatorPrinter(pace_calc,
                                                    keys_to_exclude={'sleep_start', 'pace'})
    pace_calculator_printer.print(with_sub_splits=with_sub_splits)


if __name__ == '__main__':
    main()
