import datetime

import gpxpy
from gpxpy.gpx import GPX, GPXTrackPoint


def read_gpx(filename: str) -> GPX:
    with open(filename, 'r') as f:
        return gpxpy.parse(f, version='1.1')


def save_gpx(filename: str, gpx) -> None:
    with open(filename, 'w') as f:
        f.write(gpx.to_xml())
