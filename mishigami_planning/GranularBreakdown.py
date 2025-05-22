from datetime import datetime, timedelta
from PaceCalculator import PaceCalculator
from mishigami_planning.PaceCalculatorPrinter import PaceCalculatorPrinter
from mishigami_planning.RestStop import RestStop
from mishigami_planning.Split import Split
from mishigami_planning.Utils import hours_to_pretty as hrs_prty


def print_granular_breakdown(splits: list[list[Split]],
                             initial_moving_speed: float,
                             min_moving_speed: float,
                             decay_per_split: float,
                             downtime_ratio: float,
                             start_time: datetime,
                             split_adjustment_times: list[timedelta],
                             sub_split_distances: float = 20,
                             with_sub_splits: bool = False,
                             last_split_zero_downtime: bool = True):
    curr_speed = initial_moving_speed
    _start_time = start_time
    start_mile = 0
    elapsed_time = timedelta()
    down_time = timedelta()
    moving_time = timedelta()
    adjustment_time = timedelta()
    split_adjustment_time = timedelta()

    total_distance = sum((sum(segment.distance for segment in split) for split in splits) if splits else 0)

    pace_calculator = PaceCalculator()
    pace_calculator_printer = PaceCalculatorPrinter(pace_calculator,
                                                    keys_to_exclude={'pace', 'split_speed'},
                                                    keys_to_rename={'adjustment_start': 'Rest Stop Arrival'})

    for i, split in enumerate(splits):
        pace_calculator.set_split_info(
            splits=split,
            downtime_ratio=downtime_ratio,
            start_time=_start_time,
            start_moving_speed=curr_speed,
            decay_per_split=0,
            min_moving_speed=min_moving_speed,
            no_end_downtime=last_split_zero_downtime,
            start_offset=start_mile,
            sub_split_distances=sub_split_distances
        )

        segments, res = pace_calculator.get_split_breakdown()

        pace_calculator_printer.print(with_sub_splits=with_sub_splits)
        elapsed_time += res['total_time']
        down_time += res['down_time']
        moving_time += res['moving_time']
        adjustment_time += res['adjustment_time']

        _start_time = res["end_time"]
        if i + 1 < len(splits):
            _split_adjustment_time = split_adjustment_times[i] if i < len(split_adjustment_times) else timedelta()

            print(f"{'Sleep Time':14}: {hrs_prty(_split_adjustment_time).strip():14} "
                  f"[{_split_adjustment_time.total_seconds() / 3600:7.3f} hours]", end='\n\n')

            # shift next split's start time if split adjustment time is supplied
            _start_time += _split_adjustment_time
            elapsed_time += _split_adjustment_time
            split_adjustment_time += _split_adjustment_time

        curr_speed = max(segments[-1]['moving_speed'] - decay_per_split, min_moving_speed)
        start_mile += sum(segment.distance for segment in split)

    print()
    print(f"Summary")
    print(f"{'Total Distance':14}: {total_distance:>8.3f}")
    print(f"{'Time Span':14}: {start_time:%m/%d %I:%M %p} - {_start_time:%m/%d %I:%M %p}")
    print(f"{'Moving Time':14}: {hrs_prty(moving_time).strip():14} [{moving_time.total_seconds() / 3600:7.3f} hours]")
    print(f"{'Down Time':14}: {hrs_prty(down_time).strip():14} [{down_time.total_seconds() / 3600:7.3f} hours]")
    print(f"{'Adj. Time':14}: {hrs_prty(adjustment_time).strip():14} "
          f"[{adjustment_time.total_seconds() / 3600:7.3f} hours]")
    print(f"{'Sleep Time':14}: {hrs_prty(split_adjustment_time).strip():14} "
          f"[{split_adjustment_time.total_seconds() / 3600:7.3f} hours]")
    print(f"{'Elapsed Time':14}: {hrs_prty((_start_time - start_time).total_seconds() / 3600).strip()} "
          f"[{(_start_time - start_time).total_seconds() / 3600:7.3f} hours]")
    print(f"{'Pace':14}: {total_distance / (elapsed_time.total_seconds() / 3600):>7.3f}")
    print(f"{'Distance/Day':14}: {total_distance/(elapsed_time.total_seconds() / (3600 * 24)):>7.3f}")
    print(f"{'Moving/Elapsed':14}: {moving_time / elapsed_time:>8.3%}")
    print(f"{'Down/Elapsed':14}: {down_time / elapsed_time:>8.3%}")
    print(f"{'Adj./Elapsed':14}: {adjustment_time / elapsed_time:>8.3%}")
    print(f"{'Down/Moving':14}: {down_time / moving_time:>8.3%}")
    print(f"{'Adj./Moving':14}: {adjustment_time / moving_time:>8.3%}")


def main():
    print('GRANULAR')
    segment_one = [
        Split(
            distance=114.3,
            rest_stop=RestStop(
                name="McDonald's",
                address="7170 N Teutonia Ave, Milwaukee, WI 53209",
                hours={
                    5: ' 6:00a -  9:00p',
                    6: ' 6:00a -  9:00p',
                    0: ' 6:00a -  9:00p',
                    1: ' 6:00a -  9:00p',
                    2: ' 6:00a -  9:00p',
                    3: ' 6:00a -  9:00p',
                    4: ' 6:00a -  9:00p',
                },
                alt='https://maps.app.goo.gl/HtB1C8vYKT6NPGwC8',
            )
        ),
        Split(
            distance=132.2,
            adjustment_time=timedelta(minutes=15),
            rest_stop=RestStop(
                name="Shell",
                address="1010 S Broadway, De Pere, WI 54115",
                hours={
                    5: '24hr',
                    6: '24hr',
                    0: '24hr',
                    1: '24hr',
                    2: '24hr',
                    3: '24hr',
                    4: '24hr',
                },
                alt='https://maps.app.goo.gl/ZqLUEoFBVNCbqRjTA'
            )
        ),
        Split(
            distance=147.8,
            sub_split_count=3,
            rest_stop=RestStop(
                name="bp",
                address="W365 US-2 #41, Harris, MI 49845",
                hours={
                    5: ' 6:00a - 10:00a',
                    6: ' 6:00a - 10:00a',
                    0: ' 6:00a - 10:00a',
                    1: ' 6:00a - 10:00a',
                    2: ' 6:00a - 10:00a',
                    3: ' 6:00a - 10:00a',
                    4: ' 6:00a - 10:00a',
                },
                alt='https://maps.app.goo.gl/XGN1H1cksLxMYKQq7'
            ),
        ),
        Split(
            distance=86.40-6.8,
            adjustment_time=timedelta(minutes=15),
            rest_stop=RestStop(
                name="bp",
                address="1223 US-2, Gulliver, MI 49840",
                hours={
                    5: ' 7:00a -  9:00p',
                    6: ' 7:00a -  9:00p',
                    0: ' 5:00a -  9:00p',
                    1: ' 5:00a -  9:00p',
                    2: ' 5:00a -  9:00p',
                    3: ' 5:00a -  9:00p',
                    4: ' 5:00a -  9:00p',
                },
                alt='https://maps.app.goo.gl/aPGmeEHsRerT7zc9A'
            ),
        ),
        Split(
            distance=90.8+6.8,
            rest_stop=RestStop(
                name="Best Western Harbour Pointe Lakefront",
                address='797 N State St, St Ignace, MI 49781',
                hours={
                    5: ' 3:00p - 11:00a',
                    6: ' 3:00p - 11:00a',
                    0: ' 3:00p - 11:00a',
                    1: ' 3:00p - 11:00a',
                    2: ' 3:00p - 11:00a',
                    3: ' 3:00p - 11:00a',
                    4: ' 3:00p - 11:00a',
                },
            ),
            # down_time=timedelta(minutes=36, seconds=9, microseconds=9, milliseconds=420)
        )
    ]
    segment_two = [
        Split(
            distance=125.3,
            sub_split_count=2,
            rest_stop=RestStop(
                name="Mobil",
                address="100 1st St, Elk Rapids, MI 49629",
                hours={
                    5: ' 5:00a - 11:00p',
                    6: ' 6:00a - 10:00p',
                    0: ' 5:00a - 11:00p',
                    1: ' 5:00a - 11:00p',
                    2: ' 5:00a - 11:00p',
                    3: ' 5:00a - 11:00p',
                    4: ' 5:00a - 11:00p',
                },
                alt='https://maps.app.goo.gl/RFrHK3DAkJN866Bo9'
            ),
        ),
        Split(
            distance=108.5,
            rest_stop=RestStop(
                name="Wesco (Gas Station)",
                address="75 Cypress St, Manistee, MI 49660",
                hours={
                    5: '24hr',
                    6: '24hr',
                    0: '24hr',
                    1: '24hr',
                    2: '24hr',
                    3: '24hr',
                    4: '24hr',
                },
                alt='https://maps.app.goo.gl/rwm6D7XMNBFK1scx8'
            ),
        ),
        Split
        (
            distance=130.9,
            adjustment_time=timedelta(minutes=30),
            sub_split_count=2,
            rest_stop=RestStop(
                name="CVS",
                # name="McDonald's",
                address="132 Douglas Ave, Holland, MI 49424",
                hours={
                    5: '24hr',
                    6: '24hr',
                    0: '24hr',
                    1: '24hr',
                    2: '24hr',
                    3: '24hr',
                    4: '24hr',
                },
                alt='https://maps.app.goo.gl/hK7nrRVG1G2doeeu7'
            ),
        ),
        Split
        (
            distance=100,
            rest_stop=RestStop(
                name="Barney's",
                address="10 N Thompson St, New Buffalo, MI 49117",
                hours={
                    5: ' 7:00a -  9:00p',
                    6: ' 7:00a -  9:00p',
                    0: ' 7:00a -  9:00p',
                    1: ' 7:00a -  9:00p',
                    2: ' 7:00a -  9:00p',
                    3: ' 7:00a -  9:00p',
                    4: ' 7:00a -  9:00p',
                },
                alt='https://maps.app.goo.gl/qdtBCxyiEBENdZam8'
            ),
        ),
        Split
        (
            distance=85,
            rest_stop=RestStop(
                name='Specialized Fulton',
                address='925 W Lake St, Chicago, IL 60607',
                hours={
                    5: '10:00a -  5:00p',
                    6: '11:00a -  4:00p',
                    0: '11:00a -  6:00p',
                    1: '11:00a -  6:00p',
                    2: '11:00a -  6:00p',
                    3: '11:00a -  6:00p',
                    4: '11:00a -  6:00p',
                }
            ),
            # down_time=timedelta(minutes=37, seconds=59, microseconds=0, milliseconds=650)
        ),
    ]

    initial_moving_speed = 17.0
    min_moving_speed = 15
    decay_per_split_mph = 0.2
    downtime_ratio = 5.0 / 100
    start_date = datetime(year=2025, month=6, day=19, hour=6, minute=0)
    split_adjustment_times = [timedelta(hours=8)]
    sub_split_distances = 62.14
    last_split_zero_downtime = True
    with_sub_splits = True
    print_granular_breakdown(splits=[segment_one, segment_two],
                             split_adjustment_times=split_adjustment_times,
                             initial_moving_speed=initial_moving_speed,
                             min_moving_speed=min_moving_speed,
                             decay_per_split=decay_per_split_mph,
                             downtime_ratio=downtime_ratio,
                             start_time=start_date,
                             sub_split_distances=sub_split_distances,
                             last_split_zero_downtime=last_split_zero_downtime,
                             with_sub_splits=with_sub_splits)


if __name__ == "__main__":
    main()
