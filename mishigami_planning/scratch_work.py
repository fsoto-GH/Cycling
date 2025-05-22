from mishigami_planning.PaceCalculator import PaceCalculator
from datetime import datetime

from mishigami_planning.PaceCalculatorPrinter import PaceCalculatorPrinter
from mishigami_planning.Split import Split, RestStop


def splits_from_distances(markers: list[float]):
    if len(markers) == 1:
        return markers
    res = []
    markers_w_zero = [0.0] + markers
    for i in range(len(markers_w_zero) - 1):
        res.append(markers_w_zero[i + 1] - markers_w_zero[i])
    return res


def main():
    distance = 103
    split_count = 2
    markers = [107.7, 206.3]
    split_distances = splits_from_distances(markers)

    # if splits are not defined, generate based on distance and split
    if split_distances is None or len(split_distances) == 0:
        split_distances = [distance / split_count] * split_count

    start_moving_speed = 18.0
    min_moving_speed = 15
    decay_per_split = 0.2
    sleep_times: list[float] = [0 for _ in range(len(split_distances))]

    # special sleep time designated to eat
    # sleep_times[0] = -5 / 60
    # sleep_times[1] = -5 / 60
    # sleep_times[2] = 5 / 60
    downtime_ratio = 0.1

    start_offset = 0

    start_time = datetime(year=2025, month=5, day=17, hour=5, minute=00)
    no_end_downtime = True

    splits = [
        Split(
            distance=split_distances[0],
            rest_stop=RestStop(
                name="Exxon",
                address="710 E Cass St, Joliet, IL 60432",
                hours={k: '24hrs' for k in range(7)},
            )
        ),
        Split(
            distance=split_distances[1],
            rest_stop=RestStop(
                name="Speedway",
                address="752 Indian Bdy Rd, Chesterton, IN 46304",
                hours={k: '24hrs' for k in range(7)},
            )
        ),
        # Split(
        #     distance=split_distances[2],
        #     rest_stop=RestStop(
        #         name="La Taquiza Highland Park",
        #         address="71960 1st St, Highland Park, IL 60035",
        #         hours={k: '10a - 8p' for k in range(7)},
        #     )
        # )
    ]

    pace_calc = PaceCalculator()

    # pace detail is good if you intend to sleep after a split
    pace_calc.set_split_info(splits=splits,
                             downtime_ratio=downtime_ratio,
                             start_time=start_time,
                             no_end_downtime=no_end_downtime,
                             start_offset=start_offset,
                             start_moving_speed=start_moving_speed,
                             min_moving_speed=min_moving_speed,
                             decay_per_split=decay_per_split)

    pace_calculator_printer = PaceCalculatorPrinter(pace_calc,
                                                    keys_to_exclude={'sleep_start', 'pace'})
    pace_calculator_printer.print(with_sub_splits=True)


if __name__ == '__main__':
    main()
