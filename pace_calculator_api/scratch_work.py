from datetime import datetime, timedelta

from Cycling.mishigami_planning.PaceCalculatorPrinter import PaceCalculatorPrinter
from Cycling.mishigami_planning.RestStop import RestStop
from Cycling.mishigami_planning.Split import Split
from Cycling.mishigami_planning.SubDistancePaceCalculator import SubDistancePaceCalculator

(MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY) = range(7)


def splits_from_distances(markers: list[float]):
    if len(markers) == 1:
        return markers
    res = []
    markers_w_zero = [0.0] + markers
    for i in range(len(markers_w_zero) - 1):
        res.append(markers_w_zero[i + 1] - markers_w_zero[i])
    return res


def include_mile_padding(miles: list[float], padding: float):
    # offset the miles by the padding and append and prepend miles for padding
    return [padding] + [m + padding for m in miles] + [miles[-1] + 2 * padding]


def main():
    distance = 379.6
    split_count = 5
    miles_to_start = 11.87

    markers = [65.3, 138.8, 210.5, 266.7, 353.6, 379.6]
    if miles_to_start is not None:
        markers = include_mile_padding(markers, miles_to_start)

    split_distances = splits_from_distances(markers)

    # if splits are not defined, generate based on distance and split
    if split_distances is None or len(split_distances) == 0:
        split_distances = [distance / split_count] * split_count

    start_moving_speed = 17.5
    min_moving_speed = 15
    decay_per_split = 0.0
    downtime_ratio = 0.03
    sub_split_distances = 10

    start_offset = 0

    start_time = datetime(year=2025, month=9, day=13, hour=5, minute=15)
    no_end_downtime = True

    splits = [Split(distance=split_distance) for split_distance in split_distances]

    # start edit
    splits[0].down_time = timedelta(minutes=4, seconds=19)

    splits[1].rest_stop = RestStop(
        name='Family Express',
        hours={
            SATURDAY: ' 5:00a - 12:00a',
            SUNDAY: ' 5:00a - 12:00a',
            MONDAY: ' 5:00a - 12:00a',
            TUESDAY: ' 5:00a - 12:00a',
            WEDNESDAY: ' 5:00a - 12:00a',
            THURSDAY: ' 5:00a - 12:00a',
            FRIDAY: ' 5:00a - 12:00a',
        },
        address='402 E Talmer Ave, North Judson, IN 46366',
    )
    splits[2].rest_stop = RestStop(
        name='Phillips 66',
        hours={
            SATURDAY: ' 5:00a - 10:00p',
            SUNDAY: ' 5:00a - 10:00p',
            MONDAY: ' 5:00a - 10:00p',
            TUESDAY: ' 5:00a - 10:00p',
            WEDNESDAY: ' 5:00a - 10:00p',
            THURSDAY: ' 5:00a - 10:00p',
            FRIDAY: ' 5:00a - 10:00p',
        },
        address='402 E Talmer Ave, North Judson, IN 46366',
    )
    splits[3].rest_stop = RestStop(
        name='McDonalds',
        hours={
            SATURDAY: ' 6:00a - 10:00p',
            SUNDAY: ' 6:00a - 10:00p',
            MONDAY: ' 6:00a - 10:00p',
            TUESDAY: ' 6:00a - 10:00p',
            WEDNESDAY: ' 6:00a - 10:00p',
            THURSDAY: ' 6:00a - 10:00p',
            FRIDAY: ' 6:00a - 10:00p',
        },
        address='945 E Tournament Trl, Westfield, IN 46074',
    )
    splits[3].down_time = timedelta(minutes=15)
    splits[4].rest_stop = RestStop(
        name='McClure',
        hours={
            SATURDAY: ' 24h',
            SUNDAY: ' 24h',
            MONDAY: ' 24h',
            TUESDAY: ' 24h',
            WEDNESDAY: ' 24h',
            THURSDAY: ' 24h',
            FRIDAY: ' 24h',
        },
        address='1925 18th St, Logansport, IN 46947',
    )
    splits[5].rest_stop = RestStop(
        name='Family Express',
        hours={
            SATURDAY: ' 24h',
            SUNDAY: ' 24h',
            MONDAY: ' 24h',
            TUESDAY: ' 24h',
            WEDNESDAY: ' 24h',
            THURSDAY: ' 24h',
            FRIDAY: ' 24h',
        },
        address='641 US-231, Crown Point, IN 46307',
    )

    # end penultimate split
    splits[-2].down_time = timedelta(minutes=2, seconds=0)

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
    pace_calculator_printer.print(with_sub_splits=not True)


if __name__ == '__main__':
    main()
