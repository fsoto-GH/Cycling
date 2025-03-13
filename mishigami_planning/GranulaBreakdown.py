from datetime import datetime, timedelta
from PaceCalculator import PaceCalculator


def split_breakdown(split_distances: list[list[float]],
                    sleep_times: list[float],
                    initial_mph: float,
                    min_mph: float,
                    decay_per_split_mph: float,
                    downtime_ratio: float,
                    stops: list[dict],
                    start_time: datetime):
    curr_speed = initial_mph
    _start_time = start_time
    start_mile = 0
    stop_i = 0
    elapsed_time, down_time, moving_time, sleep_time = 0, 0, 0, 0
    for i, distances in enumerate(split_distances):

        x = PaceCalculator(start_moving_pace=curr_speed,
                           min_moving_speed=curr_speed,
                           decay_per_split=0)

        _, res = x.print_summary(distances,
                                 sleep_times=[0] * len(distances),
                                 downtime_ratio=downtime_ratio,
                                 start_time=_start_time,
                                 keys_to_exclude={'sleep_start', 'sleep_time', 'split_time', 'split_speed'},
                                 keys_to_rename={'total_time': 'Elapsed Time'},
                                 start_offset=start_mile,
                                 stops=stops[stop_i:stop_i + len(distances)],
                                 no_end_downtime=i + 1 == len(split_distances))
        # print sleep time for splits except the last one
        if i + 1 < len(split_distances):
            print(f'Sleep Time: {sleep_times[i]} hours')
            sleep_time += sleep_times[i]
            elapsed_time += sleep_times[i]
        print()

        elapsed_time += res['total_time']
        down_time += res['down_time']
        moving_time += res['moving_time']

        _start_time = res["end_time"] + timedelta(hours=(sleep_times[i] if i + 1 < len(split_distances) else 0))
        curr_speed = max(curr_speed - decay_per_split_mph, min_mph)
        start_mile += sum(distances)
        stop_i = len(distances)

    print(f"{elapsed_time=:2.2f}")
    print(f"{down_time=:2.2f}")
    print(f"{moving_time=:2.2f}")
    print(f"{sleep_time=:2.2f}")
    print(f"duration={start_time:%m/%d %I:%M:%S %p}-{_start_time:%m/%d %I:%M:%S %p}")
    print(f"{moving_time / elapsed_time=:2.2%}")
    print(f"{down_time / moving_time=:2.2%}")
    print(f"{(down_time + sleep_time) / moving_time=:2.2%}")


def main():
    initial_mph = 17.6
    min_mph = 15.5
    decay_per_split_mph = 2
    downtime_ratio = 8.5 / 100
    start_date = datetime(year=2025, month=7, day=12, hour=6, minute=0)

    distances = [
        [571.5/5] * 5,
        [549.7/5] * 5,
    ]
    sleep_times = [11]
    stops = [
        {
            'name': "McDonald's",
            'address': "7170 N Teutonia Ave, Milwaukee, WI 53209",
            'hours': {
                5: ' 6:00a -  9:00p',
                6: ' 6:00a -  9:00p',
                0: ' 6:00a -  9:00p',
                1: ' 6:00a -  9:00p'
            },
        },
        {
            'name': "Shell",
            'address': "1010 S Broadway, De Pere, WI 54115",
            'hours': {
                5: '24hr',
                6: '24hr',
                0: '24hr',
                1: '24hr',
            }
        },
        {
            'name': "bp",
            'address': "W365 US-2 #41, Harris, MI 49845",
            'hours': {
                5: ' 6:00a -  1:00a',
                6: ' 6:00a -  1:00a',
                0: ' 6:00a -  1:00a',
                1: ' 6:00a -  1:00a',
            }
        },
        {
            'name': "bp",
            'address': "1223 US-2, Gulliver, MI 49840",
            'hours': {
                5: ' 7:00a -  9:00p',
                6: ' 7:00a -  9:00p',
                0: ' 5:00a -  9:00p',
                1: ' 5:00a -  9:00p',
            }
        },
        {
            'name': "Best Western Harbour Pointe Lakefront",
            'address': '797 N State St, St Ignace, MI 49781',
            'hours': {
                5: '3:00p-11:00a',
                6: ' 3:00p - 11:00a',
                0: ' 3:00p - 11:00a',
                1: ' 3:00p - 11:00a',
            }
        },
        {
            'name': "Mobil",
            'address': "100 1st St, Elk Rapids, MI 49629",
            'hours': {
                5: ' 5:00a - 11:00p',
                6: ' 6:00a - 10:00p',
                0: ' 5:00a - 11:00p',
                1: ' 5:00a - 11:00p',
            }
        },
        {
            'name': "Wesco (Gas Station)",
            'address': "75 Cypress St, Manistee, MI 49660",
            'hours': {
                5: '24hr',
                6: '24hr',
                0: '24hr',
                1: '24hr',
            }
        },
        {
            'name': "McDonald's",
            'address': "213 N River Ave, Holland, MI 49424",
            'hours': {
                5: '24hr',
                6: '24hr',
                0: '24hr',
                1: '24hr',
            },
        },
        {
            'name': "Barney's",
            'address': "10 N Thompson St, New Buffalo, MI 49117",
            'hours': {
                5: '7:00a-9:00p',
                6: ' 7:00a -  9:00p',
                0: ' 7:00a -  9:00p',
                1: ' 7:00a -  9:00p',
            },
        },
        {
            'name': 'Specialized Fulton',
            'address': '925 W Lake St, Chicago, IL 60607',
            'hours': {
                5: '10:00a -  5:00p',
                6: '11:00a -  4:00p',
                0: '11:00a -  6:00p',
                1: '11:00a -  6:00p',
            }
        }
    ]

    # print('EVEN SPLIT')
    # split_breakdown(split_distances=distances,
    #                 sleep_times=sleep_times,
    #                 initial_mph=initial_mph,
    #                 min_mph=min_mph,
    #                 decay_per_split_mph=decay_per_split_mph,
    #                 downtime_ratio=downtime_ratio,
    #                 stops=stops,
    #                 start_time=start_date)

    print('GRANULAR')
    distances = [
        [114.3, 132.2, 147.8, 86.40, 90.8],
        [125.3, 108.5, 130.9, 100, 85]
    ]
    split_breakdown(split_distances=distances,
                    sleep_times=sleep_times,
                    initial_mph=initial_mph,
                    min_mph=min_mph,
                    decay_per_split_mph=decay_per_split_mph,
                    downtime_ratio=downtime_ratio,
                    stops=stops,
                    start_time=start_date)


if __name__ == "__main__":
    main()
