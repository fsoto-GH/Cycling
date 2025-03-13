import dataclasses
from datetime import timedelta, date


def weeks_to(day: date) -> list[date]:
    curr = day
    today = date.today()

    res = []
    if curr < today:
        return res

    days_between = today - curr
    res = [curr + timedelta(days=-i) for i in range(0, -days_between.days, 7)[::-1]]

    return res


def get_weeks_before(weeks: list[date], season_start: date):
    return [week for week in weeks if week < season_start]


def compute_schedule(weeks: list[date], weeks_to_taper: int, taper_reduction: float, season_start: date):
    if len(weeks) < weeks_to_taper:
        raise ValueError("Not enough time to taper")

    if taper_reduction > 1:
        raise ValueError("Taper reduction must be in the range of (0, 1)")

    off_season_weeks = get_weeks_before(weeks, season_start)
    training_weeks = weeks[len(off_season_weeks):-(weeks_to_taper + 1)]
    taper_weeks = weeks[-(weeks_to_taper + 1): -1]
    event_day = weeks[-1]

    return {
        "off_season": off_season_weeks,
        "training": training_weeks,
        "taper": taper_weeks,
        "event_day": [event_day]
    }


@dataclasses.dataclass
class TrainingWeek:
    week: date
    distance: float


def main():
    mishigami_start = date(year=2025, month=7, day=12)
    season_start = date(year=2025, month=3, day=22)
    res = weeks_to(mishigami_start)

    schedule = compute_schedule(
        res,
        weeks_to_taper=2,
        taper_reduction=0.2,
        season_start=season_start
    )

    for component in schedule:
        for _date in schedule[component]:
            print(f"{component:<10s}: {_date:%m/%d/%Y}")
        print()


if __name__ == '__main__':
    main()
