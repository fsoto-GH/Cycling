from datetime import datetime, timedelta

# NOTE: Python dictionaries preserve order as of 3.7
from mishigami_planning.Split import Split
from mishigami_planning.Utils import split_into_chunks


def compute_sub_splits(total_distance: float,
                       down_time_ratio: float,
                       moving_speed: float,
                       start_time: datetime,
                       start_offset: float,
                       sub_split_distances: float = 20):
    sub_split_distances = split_into_chunks(total_distance, sub_split_distances)

    res = []
    for sub_split_distance in sub_split_distances:
        sub_split_time = sub_split_distance / moving_speed
        res.append({
            "distance": sub_split_distance,
            "span": f"{start_offset:>7.2f}, {(start_offset := start_offset + sub_split_distance):>7.2f}",
            "moving_speed": moving_speed,
            "sleep_time": 0,
            "moving_time": sub_split_time,
            "split_time": sub_split_time * (1 + down_time_ratio),
            "split_speed": moving_speed,
            "down_time": sub_split_time * down_time_ratio,
            "total_time": sub_split_time * (1 + down_time_ratio),
            "pace": moving_speed,
            "start_time": start_time,
            "sleep_start": start_time + timedelta(hours=0),
            "end_time": (start_time := (start_time + timedelta(hours=sub_split_time * (1 + down_time_ratio)))),
            "stop": None
        })

    return res


class PaceCalculator:
    def __init__(self):
        """
        Represents a pace calculator to be used for split distance simulations.
        """
        self.sub_split_distances = 20
        self.start_moving_speed: float = 0
        self.min_moving_speed: float = 0
        self.segments: list[Split] = []
        self.downtime_ratio: float = 0
        self.stops: list[dict[str: str]] = []
        self.decay_per_split: float = 0
        self.start_time: datetime = datetime.today()
        self.start_offset: float = 0
        self.no_end_downtime: bool = False

    def set_split_info(self,
                       start_moving_speed: float,
                       min_moving_speed: float,
                       splits: list[Split],
                       downtime_ratio: float = 0,
                       stops: list[dict[str: str]] | None = None,
                       decay_per_split: float = 0,
                       start_time: datetime | None = None,
                       start_offset: float = 0,
                       no_end_downtime: bool = False,
                       sub_split_distances: float = 20):
        """
        A
        :param sub_split_distances:
        :param splits:
        :param downtime_ratio:
        :param stops:
        :param start_time:
        :param start_offset:
        :param no_end_downtime:
        :param start_moving_speed: the expected moving time speed
        :param min_moving_speed: the minimum moving speed (lower bound for decay)
        :param decay_per_split: how much speed is expected to drop per split
        :return:
        """
        self.start_moving_speed = start_moving_speed
        self.min_moving_speed = min_moving_speed
        self.decay_per_split = decay_per_split
        self.segments = splits
        self.downtime_ratio = downtime_ratio
        self.stops = stops
        self.start_time = start_time or datetime.today()
        self.start_offset = start_offset
        self.no_end_downtime = no_end_downtime
        self.sub_split_distances = sub_split_distances

    def __compute_split_details(self):
        times = self.__compute_time()
        start_time = self.start_time or datetime.today()

        res = []
        _start_offset = self.start_offset
        for i, (segment, (moving_time, moving_speed)) in enumerate(zip(self.segments, times), start=1):
            _down_time_ratio = self.downtime_ratio
            if self.no_end_downtime:
                _down_time_ratio = self.downtime_ratio if i < len(self.segments) else 0

            _split_time = moving_time * (1 + _down_time_ratio)
            if segment.down_time is not None:
                _split_time = moving_time + segment.down_time

            _sleep_time = timedelta(hours=0)
            if segment.sleep_time is not None:
                _sleep_time = segment.sleep_time

            _moving_speed = moving_speed
            if segment.moving_speed is not None:
                _moving_speed = segment.moving_speed

            _res = {
                "distance": segment.distance,
                "sub_splits": compute_sub_splits(
                    total_distance=segment.distance,
                    down_time_ratio=_down_time_ratio,
                    moving_speed=_moving_speed,
                    start_time=start_time,
                    start_offset=_start_offset,
                    sub_split_distances=self.sub_split_distances),
                "span": f"{_start_offset:>7.2f}, {(_start_offset := _start_offset + segment.distance):>7.2f}",
                "moving_speed": _moving_speed,
                "sleep_time": _sleep_time,
                "moving_time": moving_time,
                "split_time": _split_time,
                "split_speed": segment.distance / (_split_time.total_seconds() / 3600),
                "down_time":  moving_time * _down_time_ratio if segment.down_time is None else segment.down_time,
                "total_time": _split_time + _sleep_time,
                "pace": segment.distance / ((_split_time + _sleep_time).total_seconds() / 3600),
                "start_time": start_time,
                "sleep_start": start_time + _split_time,
                "end_time": (start_time := start_time + _split_time + _sleep_time),
                "stop": segment.rest_stop
            }

            if self.stops and i <= len(self.stops):
                _res['stop'] = self.stops[i - 1]
            res.append(_res)

        return res

    def __compute_time(self):
        """
        Returns the split time given the moving speed and decay in decimal hours.
        :return: list of time in decimal hour per split
        """
        split_times: list[tuple[timedelta, float]] = []

        curr_speed = self.start_moving_speed
        for i, segment in enumerate(self.segments, start=1):
            if segment.moving_speed is None:
                split_times.append((timedelta(hours=segment.distance / curr_speed), curr_speed))
                curr_speed = max(curr_speed - self.decay_per_split, self.min_moving_speed)
            else:
                split_times.append((timedelta(hours=segment.distance / segment.moving_speed), segment.moving_speed))

        return split_times

    def get_split_breakdown(self):
        """
        Prints a data table that describes the split details and extends summaries.
        
        :param no_end_downtime:
        :param stops: list of stops to map each split to as a rest stop
        :param start_offset: a distance to offset the start, end span

        :param start_time: an optional start to compute expected end times
        :param splits: the designated split distances
        :param sleep_times: a list of float times to include in split times. This can add sleep or adjust rest time.
        :param downtime_ratio: a ratio representing how much time will be downtime for a given moving time. For 2h of
        moving time, a downtime ratio of .5 will generate a downtime of 0.5h so the split will be 2.5h long.
        For example, 10hr and a downtime_ratio of 0.1 = 10hrs of moving time and 1hr of downtime (like pit stops)
        :return: a list of each split's details and an object with the summarized data points
        """
        split_details = self.__compute_split_details()

        summary = self.compute_summary(split_details)

        return split_details, summary

    def compute_summary(self, split_details) -> dict[str: any]:
        total_distance: float = 0
        total_moving_time: timedelta = timedelta(hours=0)
        total_down_time: timedelta = timedelta(hours=0)
        total_split_time: timedelta = timedelta(hours=0)
        total_sleep_time: timedelta = timedelta(hours=0)
        total_time: timedelta = timedelta(hours=0)
        total_pace: float = 0
        start_time: datetime = self.start_time or datetime.today()
        end_time: datetime = start_time

        for i, split in enumerate(split_details):
            total_distance += split['distance']
            total_down_time += split['down_time']
            total_moving_time += split['moving_time']
            total_split_time += split['split_time']
            total_sleep_time += split['sleep_time']
            total_time += split['total_time']
            total_pace += split['pace']
            end_time += split['total_time']

        return {
            "distance": total_distance,
            "span": f"{self.start_offset:>7.2f}, {self.start_offset + total_distance:>7.2f}",
            "moving_speed": total_distance / (total_moving_time.total_seconds() / 3600),
            "moving_time": total_moving_time,
            "down_time": total_down_time,
            "split_time": total_split_time,
            "split_speed": total_distance / (total_split_time.total_seconds() / 3600),
            "sleep_time": total_sleep_time,
            "total_time": total_time,
            "pace": total_distance / (total_time.total_seconds() / 3600),
            "start_time": start_time,
            "sleep_start": None,
            "end_time": end_time
        }


def main():
    """
    Entry point to subroutine that computes double split details for a given interval of downtime ratio.
    :return: None
    """
    initial_mph = 17.6
    min_mph = 16.8
    decay_per_split_mph = 1

    distances = [Split(distance=571.5), Split(distance=549.5)]
    downtime_ratio = 0

    start_date = datetime(year=2025, month=7, day=12, hour=8, minute=0)

    pace_calculator = PaceCalculator()
    pace_calculator.set_split_info(
        start_moving_speed=initial_mph,
        min_moving_speed=min_mph,
        decay_per_split=decay_per_split_mph,
        splits=distances,
        start_time=start_date,
        downtime_ratio=downtime_ratio,
    )

    splits, summary = pace_calculator.get_split_breakdown()
    print(splits)


if __name__ == "__main__":
    main()
