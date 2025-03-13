import datetime
import math


def should_show_field(field_key: str, keys_to_exclude: set[str]):
    return field_key not in keys_to_exclude


def safe_field_rename(field_key: str, safe_name: str, keys_to_rename: dict[str: str]):
    if field_key in keys_to_rename:
        return keys_to_rename[field_key]
    return safe_name


def format_field(val: str, formatting: str):
    return f'{val:{formatting}}'


def compute_distances(distance: float, split_count: int) -> list[float]:
    even_split = distance // split_count
    rounded_split = round_nearest_5(even_split)
    split_distance: list[float] = [rounded_split for _ in range(split_count)]

    rounded_dist = rounded_split * split_count
    if rounded_dist > distance:
        # check if rounded is over distance and adjust last split if so
        split_distance[-1] = distance - rounded_split * (split_count - 1)
    else:
        # append remaining diff to first split for fatigue
        split_distance[0] += distance - rounded_dist

    return split_distance


def hours_to_pretty(decimal_hours: float):
    """
    Converts decimal hours to days, hours, minutes, and seconds.
    Leading zeroes can be omitted and last precision can be reduced to minutes.
    The last precision is rounded.

    :param decimal_hours: the amount to convert
    :return: string representing the day, hour, minute, and second of the decimal hours
    """
    days = decimal_hours // 24
    hours = decimal_hours % 24
    minutes = (decimal_hours - int(decimal_hours)) * 60
    seconds = (minutes - int(minutes)) * 60

    return f"{math.floor(days):2d}d {math.floor(hours):2d}h {math.floor(minutes):2d}m {seconds:5.2f}s"


def days_hours_minutes(td):
    return f"{td.days}, {td.seconds // 3600}, {(td.seconds // 60) % 60}"


def round_nearest_5(x: float):
    return int(5 * round(x / 5))


# NOTE: Python dictionaries preserve order as of 3.7
class PaceCalculator:
    FIELD_PROPS = {
        'distance': {
            "name": "Distance",
            "header_formatting": ">8s",
            "value_formatting": '8.2f',
            "width": 8
        },
        'span': {
            "name": f"{'Start':>7s}, {'End':>7s}",
            "header_formatting": "<16s",
            "value_formatting": '16s',
            "width": 16
        },
        'moving_speed': {
            "header_formatting": ">12s",
            "name": "Moving Speed",
            "value_formatting": '12.2f',
            "width": 12
        },
        'moving_time': {
            "name": "Moving Time",
            "header_formatting": ">18s",
            "value_formatting": '18s',
            "transformer": hours_to_pretty,
            "width": 18
        },
        'down_time': {
            "name": "Down Time",
            "header_formatting": ">18s",
            "value_formatting": '18s',
            "transformer": hours_to_pretty,
            "width": 18
        },
        'split_time': {
            "name": "Split Time",
            "header_formatting": ">18s",
            "value_formatting": '18s',
            "transformer": hours_to_pretty,
            "width": 18
        },
        'split_speed': {
            "name": "Split Speed",
            "header_formatting": ">11s",
            "value_formatting": '11.2f',
            "width": 11
        },
        'sleep_time': {
            "name": "Sleep Time",
            "header_formatting": ">18s",
            "value_formatting": '18s',
            "transformer": hours_to_pretty,
            "width": 18
        },
        'total_time': {
            "name": "Total Time",
            "header_formatting": ">18s",
            "value_formatting": '18s',
            "transformer": hours_to_pretty,
            "width": 18
        },
        'pace': {
            "name": "Pace",
            "header_formatting": ">5s",
            "value_formatting": '5.2f',
            "width": 5
        },
        'start_time': {
            "name": "Start Time",
            "header_formatting": ">17s",
            "value_formatting": '%m/%d %I:%M:%S %p',
            "width": 17
        },
        'sleep_start': {
            "name": "Sleep Start",
            "header_formatting": ">17s",
            "value_formatting": '%m/%d %I:%M:%S %p',
            "width": 17
        },
        'end_time': {
            "name": "End Time",
            "header_formatting": ">17s",
            "value_formatting": '%m/%d %I:%M:%S %p',
            "width": 17
        },
    }
    LOCATION_HEADERS = {
        'rest_stop_name': {
            "name": "Rest Stop Name",
            "header_formatting": "<20s",
            "value_formatting": '<20s',
            "width": 20
        },
        'rest_stop_hours': {
            "name": "Rest Stop Hours",
            "header_formatting": "<15s",
            "value_formatting": '>15s',
            "width": 15
        },
        'rest_stop_address': {
            "name": "Rest Stop Address",
            "header_formatting": ">40s",
            "value_formatting": '>40s',
            "width": 40
        },
    }
    SPACER = ' | '

    def __init__(self, start_moving_pace: float, min_moving_speed: float, decay_per_split: float = 1):
        """
        Represents a pace calculator to be used for split distance simulations.

        :param start_moving_pace: the expected moving time speed
        :param min_moving_speed: the minimum moving speed (lower bound for decay)
        :param decay_per_split: how much speed is expected to drop per split
        """
        self.start_moving_pace = start_moving_pace
        self.min_moving_speed = min_moving_speed
        self.decay_per_split = decay_per_split

    def compute_split_details(self,
                              distances: list[float],
                              sleep_time: list[float],
                              downtime_ratio: float,
                              start_time: datetime.datetime = None,
                              start_offset: float = 0,
                              no_end_downtime: bool = False):
        times = self.compute_time(distances)
        if start_time is None:
            start_time = datetime.datetime.today()

        res = []
        _d = start_offset
        for i, (distance, (moving_time, moving_speed)) in enumerate(zip(distances, times), start=1):
            _sleep_time = sleep_time[i - 1] if i < len(distances) else 0

            _down_time_ratio = downtime_ratio
            if no_end_downtime:
                _down_time_ratio = downtime_ratio if i < len(distances) else 0

            # represents moving time with refueling consideration
            split_time = moving_time * (1 + _down_time_ratio)
            _res = {
                "distance": distance,
                "span": f"{_d:>7.2f}, {(_d := _d + distance):>7.2f}",
                "moving_speed": moving_speed,
                "sleep_time": _sleep_time,
                "moving_time": moving_time,
                "split_time": split_time,
                "split_speed": distance / split_time,
                "down_time": moving_time * _down_time_ratio,
                "total_time": split_time + _sleep_time,
                "pace": distance / (split_time + _sleep_time),
                "start_time": start_time,
                "sleep_start": start_time + datetime.timedelta(hours=split_time),
                "end_time": (start_time := start_time + datetime.timedelta(hours=(split_time + _sleep_time)))
            }
            res.append(_res)

        return res

    def compute_time(self, split_distance: list[float]):
        """
        Returns the split time given the moving speed and decay in decimal hours.
        :param split_distance: distance per split in order of completion
        :return: list of time in decimal hour per split
        """
        split_times: list[tuple[float, float]] = []

        curr_speed = self.start_moving_pace
        for i, distance in enumerate(split_distance, start=1):
            split_times.append((distance / curr_speed, curr_speed))
            curr_speed = max(curr_speed - self.decay_per_split, self.min_moving_speed)

        return split_times

    def print_summary(self,
                      distances,
                      sleep_times: list[float],
                      downtime_ratio: float,
                      start_time: datetime.datetime = None,
                      keys_to_exclude: set[str] = None,
                      keys_to_rename: dict[str: str] = None,
                      start_offset: float = 0,
                      stops: list[dict] = None,
                      no_end_downtime: bool = False):
        """
        Prints a data table that describes the split details and extends summaries.
        
        :param no_end_downtime:
        :param stops: list of stops to map each split to as a rest stop
        :param start_offset: a distance to offset the start, end span
        :param keys_to_exclude: fields by key to remove from printing
        :param keys_to_rename: a dictionary containing fields by key to rename
        :param start_time: an optional start to compute expected end times
        :param distances: the designated split distances
        :param sleep_times: the amount of sleep time after a split is complete
        :param downtime_ratio: a ratio (0, 1) representing how much time will be downtime for a given moving time
        For example, 10hr and a downtime_ratio of 0.1 = 10hrs of moving time and 1hr of downtime (like pit stops)
        :return: a list of each split's details and an object with the summarized data points
        """
        if keys_to_rename is None:
            keys_to_rename = {}

        if keys_to_exclude is None:
            keys_to_exclude = set()

        split_details = self.compute_split_details(distances,
                                                   sleep_times,
                                                   downtime_ratio,
                                                   start_time,
                                                   start_offset=start_offset,
                                                   no_end_downtime=no_end_downtime)

        field_keys_showing = self.exposed_fields(keys_to_exclude, stops)

        # header
        self.print_header(field_keys_showing, keys_to_rename)

        dash_count = self.compute_dash_count(field_keys_showing, stops)
        print('-' * dash_count)

        # details
        summary = self.print_details(split_details,
                                     field_keys_showing,
                                     stops,
                                     start_time=start_time,
                                     start_offset=start_offset)
        print('-' * dash_count)

        # footer
        self.print_footer(summary, keys_to_exclude)

        print(f"{'Moving/Elapsed':14}: "
              f"{(summary['moving_time'] / summary['total_time'] if summary['total_time'] != 0 else 0):0.2%}")
        print(f"{'Down/Moving':14}: {summary['down_time'] / summary['moving_time']:0.2%}")
        print(f"{'Elapsed Time':14}: {summary['total_time']:2.2f} hours")

        return split_details, summary

    def exposed_fields(self, keys_to_exclude: set[str], stops: list[dict]):
        field_keys_showing = set(self.FIELD_PROPS.keys())
        if stops:
            field_keys_showing |= set(self.LOCATION_HEADERS.keys())

        field_keys_showing -= keys_to_exclude

        return field_keys_showing

    def compute_dash_count(self, field_keys_showing: set[str], stops: list[dict]):
        w = 'width'
        spacers_spacing = len(self.SPACER) * (len(field_keys_showing) - 1)
        base_headers = sum(self.FIELD_PROPS[k][w] for k in field_keys_showing if k in self.FIELD_PROPS)
        location_headers = sum(self.LOCATION_HEADERS[k][w] for k in field_keys_showing if k in self.LOCATION_HEADERS)
        return base_headers + spacers_spacing + (location_headers if stops else 0)

    def print_footer(self, summary: dict[str: [str | float | datetime.datetime]], keys_to_exclude: set[str]):
        res = []
        for key in self.FIELD_PROPS:
            if key not in keys_to_exclude:
                val = summary[key]
                is_filler = type(val) == str and set(val) == {'-'}
                if 'transformer' in self.FIELD_PROPS[key] and not is_filler:
                    res.append(self.FIELD_PROPS[key]['transformer'](summary[key]))
                elif is_filler:
                    res.append(format_field(val=val, formatting=self.FIELD_PROPS[key]['header_formatting']))
                else:
                    res.append(format_field(val=val, formatting=self.FIELD_PROPS[key]['value_formatting']))

        print(self.SPACER.join(res))

    def print_details(self,
                      split_details: list[dict[str: any]],
                      field_keys_showing: set[str],
                      stops: list[dict],
                      start_time: datetime.datetime = None,
                      start_offset: float = 0,
                      no_end_downtime: bool = False) -> dict[str: any]:
        total_distance: float = 0
        total_moving_time: float = 0
        total_down_time: float = 0
        total_split_time: float = 0
        total_sleep_time: float = 0
        total_time: float = 0
        total_pace: float = 0
        start_time: datetime.datetime = start_time or datetime.datetime.today()
        end_time: datetime.datetime = start_time

        for i, split in enumerate(split_details):
            total_distance += split['distance']
            total_down_time += split['down_time']
            total_moving_time += split['moving_time']
            total_split_time += split['split_time']
            total_sleep_time += split['sleep_time']
            total_time += split['total_time']
            total_pace += split['pace']
            end_time += datetime.timedelta(hours=split['total_time'])

            self.print_detail(split, field_keys_showing, stops[i] if stops and i < len(stops) else {})

        return {
            "distance": total_distance,
            "span": f"{start_offset:>7.2f}, {start_offset + total_distance:>7.2f}",
            "moving_speed": total_distance / total_moving_time if total_moving_time != 0 else 0,
            "moving_time": total_moving_time,
            "down_time": total_down_time,
            "split_time": total_split_time,
            "split_speed": total_distance / total_split_time if total_split_time != 0 else 0,
            "sleep_time": total_sleep_time,
            "total_time": total_time,
            "pace": total_distance / total_time if total_time != 0 else 0,
            "start_time": start_time,
            "sleep_start": f"{'-' * self.FIELD_PROPS['sleep_start']['width']}",
            "end_time": end_time
        }

    def print_header(self, field_keys_showing: set[str],
                     keys_to_rename: dict[str: str]):
        res = [format_field(val=_v['name'] if _k not in keys_to_rename else keys_to_rename[_k][:_v['width']],
                            formatting=f"{_v['header_formatting']}")
               for _k, _v in self.FIELD_PROPS.items() if _k in field_keys_showing]

        res_2 = [format_field(val=_v['name'] if _k not in keys_to_rename else keys_to_rename[_k][:_v['width']],
                              formatting=f"{_v['header_formatting']}")
                 for _k, _v in self.LOCATION_HEADERS.items() if _k in field_keys_showing]
        print(self.SPACER.join(res + res_2))

    def print_detail(self,
                     split: dict[str, any],
                     field_keys_showing: set[str],
                     stop: dict):
        res = []
        for key in self.FIELD_PROPS:
            if key in field_keys_showing:
                _v = split[key]
                if 'transformer' in self.FIELD_PROPS[key]:
                    _v = self.FIELD_PROPS[key]['transformer'](split[key])

                res.append(format_field(val=_v, formatting=self.FIELD_PROPS[key]['value_formatting']))

        for key in self.LOCATION_HEADERS:
            if key in field_keys_showing:
                _v = ''
                if (_k := key.split('_')[-1]) in stop:
                    _v = stop[_k]

                    if _k == 'hours':
                        d: datetime.datetime = split['end_time']
                        _v = _v[d.weekday()]
                        res.append(format_field(val=_v[:15], formatting=self.LOCATION_HEADERS[key]['value_formatting']))
                    else:
                        res.append(format_field(val=_v[:self.LOCATION_HEADERS[key]['width']],
                                                formatting=self.LOCATION_HEADERS[key]['value_formatting']))
                else:
                    res.append(format_field(val='',
                                            formatting=self.LOCATION_HEADERS[key]['value_formatting']))

        print(self.SPACER.join(res))


def pace_calculator(l_ratio: float, u_ratio: float,
                    initial_mph: float, min_mph: float, decay_per_split_mph: float,
                    distances: list[float], sleep_times: list[float],
                    start_date: datetime,
                    step: float = 0.01):
    if len(sleep_times) == 0:
        raise ValueError('Sleep time must be defined. Enter zeros if you want no sleep time between splits')

    l_ratio, u_ratio = min(l_ratio, u_ratio), max(l_ratio, u_ratio)

    # need to do a bit of data analysis
    x = PaceCalculator(start_moving_pace=initial_mph,
                       min_moving_speed=min_mph,
                       decay_per_split=decay_per_split_mph)

    if l_ratio == u_ratio:
        return [x.print_summary(
            distances=distances,
            sleep_times=sleep_times,
            downtime_ratio=l_ratio,
            start_time=start_date,
        )]

    res = []
    i = 0
    while l_ratio <= (u_ratio + step / 2):
        details = x.print_summary(distances=distances,
                                  sleep_times=sleep_times,
                                  downtime_ratio=l_ratio,
                                  start_time=start_date)
        print()  # space
        res.append(details)
        l_ratio += step
        i += 1

    return res


def main():
    initial_mph = 17.6
    min_mph = 16.8
    decay_per_split_mph = 1

    distances = [571.5, 549.5]
    sleep_times = [11]

    start_date = datetime.datetime(year=2025, month=7, day=12, hour=8, minute=0)

    paces = pace_calculator(
        8.5 / 100,
        8.5 / 100,
        initial_mph,
        min_mph,
        decay_per_split_mph,
        distances,
        sleep_times,
        start_date,
        step=5 / 1000)


if __name__ == "__main__":
    main()
    start = datetime.datetime(year=2025, month=7, day=12, hour=8)
    end = datetime.datetime(year=2025, month=7, day=15, hour=17, minute=20)

    sleep_time = 11
    elapsed_time = end - start
    elapsed_hours = elapsed_time.total_seconds() / 3600
    moving_time = (24 + 8.5) + (24 + 8.75)
    down_time = + 2.75 + 2 + 1/3

    print("Adjusted Values for Last Down Time Break")
    print(f"{moving_time / elapsed_hours=:2.2%}")
    print(f"{down_time / moving_time=:2.2%}")
    print(f"{(down_time + sleep_time) / moving_time=:2.2%}")
    print(f"{elapsed_hours=:2.2f}")
    print(f"{moving_time=:2.2f}")
    print(f"{down_time=:2.2f}")
