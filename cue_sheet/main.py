from datetime import timedelta

from Cycling.cue_sheet.DetailLines import START, FINISH, DetailLine, RestDetailLine, RestOptionalDetailLine, \
    KOMDetailLine, KOMOptionalDetailLine, LEGEND_DESCRIPTION, LEGEND
from Cycling.mishigami_planning.Utils import splits_from_distances


def assemble(markers: list[DetailLine]):
    start, end = 0, len(markers) - 1
    if markers[0].legend_key == START:
        start = 1
    if markers[-1].legend_key == FINISH:
        end = len(markers) - 2

    splits = splits_from_distances([p.mile_mark for p in markers[start:end]])

    return splits


def main():
    details = [
        DetailLine(START, 0+20.23, None, "Double Clutch Brewing Company", "Start at 8:00a (shift of 20.23mi)"),
        RestOptionalDetailLine(42.5+20.23, 42.5, "Speedway", "24h", "10:25a"),
        KOMDetailLine(46.9+20.23, 1.54, "Running Roberts", 30.3, 0, "W", timedelta(minutes=1, seconds=19)),
        RestDetailLine(78.6+20.23, 36.1, "Phillips 66", "24h", "12:40p"),
        KOMOptionalDetailLine(91.7+20.23, 0.7, "Gregg's Landing Cyp. to Broad.", 32.1, -0.4, "N", timedelta(minutes=1, seconds=19)),
        KOMOptionalDetailLine(92.2+20.23, 1.3, "Gregg's Pkwy Sprint E", 30.0, 0, "E", timedelta(minutes=2, seconds=36)),
        DetailLine(FINISH, 124.6+20.23, 46, "Double Clutch Brewing Company", "End at 3:25p"),
    ]

    print(f"{'LEGEND':-^40}")
    for key in LEGEND_DESCRIPTION:
        print(f"{LEGEND[key]}: {LEGEND_DESCRIPTION[key]}")
    print(f"{'':-^40}")
    for detail in details:
        print(detail)
        print()


if __name__ == '__main__':
    main()
