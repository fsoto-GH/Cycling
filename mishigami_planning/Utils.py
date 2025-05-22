import math
from datetime import timedelta


def should_show_field(field_key: str, keys_to_exclude: set[str]):
    return field_key not in keys_to_exclude


def safe_field_rename(field_key: str, safe_name: str, keys_to_rename: dict[str: str]):
    if field_key in keys_to_rename:
        return keys_to_rename[field_key]
    return safe_name


def format_field(val: str, formatting: str):
    return f'{val:{formatting}}'


def split_into_chunks(x, n):
    full_chunks = int(x // n)
    remainder = x % n
    return [n] * full_chunks + ([remainder] if remainder else [])


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


def hours_to_pretty(hours_timedelta: timedelta | float):
    """
    Converts decimal hours to days, hours, minutes, and seconds.
    Leading zeroes can be omitted and last precision can be reduced to minutes.
    The last precision is rounded.

    :param hours_timedelta: the amount to convert
    :return: string representing the day, hour, minute, and second of the decimal hours
    """

    if type(hours_timedelta) == timedelta:
        is_neg = hours_timedelta.total_seconds() < 0
        decimal_hours = hours_timedelta.total_seconds() / 3600
    else:
        is_neg = hours_timedelta < 0
        decimal_hours = hours_timedelta

    if is_neg:
        decimal_hours *= -1
    days = decimal_hours // 24
    hours = decimal_hours % 24
    minutes = (decimal_hours - int(decimal_hours)) * 60
    seconds = (minutes - int(minutes)) * 60

    return f"{'-' if is_neg else ' '}{math.floor(days):2d}d {math.floor(hours):2d}h {math.floor(minutes):2d}m {seconds:5.2f}s"


def days_hours_minutes(td: timedelta):
    return f"{td.days}, {td.seconds // 3600}, {(td.seconds // 60) % 60}"


def round_nearest_5(x: float):
    return int(5 * round(x / 5))
