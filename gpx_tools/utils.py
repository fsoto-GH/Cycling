import gpxpy
from gpxpy.gpx import GPX


def read_gpx(filename) -> GPX:
    with open(filename, 'r') as f:
        return gpxpy.parse(f, version='1.1')


def save_gpx(filename, gpx) -> None:
    with open(filename, 'w') as f:
        f.write(gpx.to_xml())
