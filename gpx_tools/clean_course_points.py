from gpxpy.gpx import GPX, GPXRoutePoint, GPXWaypoint
import re

from gpx_tools.utils import read_gpx, save_gpx


def get_waypoints(track: GPX, reg):
    """
    This subroutine returns waypoints matching regular expression.
    :param track: Track containing waypoints to filter.
    :param reg: The regular expression to filter waypoints on.
    :return: A GPXTrack object that excludes the waypoints that match the regular expression or all.
    """
    matcher = re.compile(reg)
    return [waypoint for waypoint in track.waypoints if matcher.match(waypoint.name)]


def get_waypoints_by_type(track: GPX, wp_type: str):
    return [waypoint for waypoint in track.waypoints if waypoint.type.lower() == wp_type.lower()]


def get_route_points(track: GPX, reg):
    matcher = re.compile(reg)
    return [point for point in track.routes[0].points if matcher.match(point.name)]


def get_route_points_by_type(track: GPX, wp_type: str, wp_type_override: str = None):
    route_points = [point for point in track.routes[0].points if point.name.lower() == wp_type.lower()]
    route_points = set_route_point_type(route_points, wp_type_override or wp_type)
    return set_route_point_name(route_points)


def set_route_point_type(points: list[GPXRoutePoint], wp_type: str):
    for p in points:
        p.type = wp_type
    return points


def set_route_point_name(points: list[GPXRoutePoint]):
    for p in points:
        p.name = p.comment
    return points


def set_waypoint_point_type(waypoints: list[GPXWaypoint], wp_type: str):
    for p in waypoints:
        p.type = wp_type
    return waypoints


def from_single_file(filename: str):
    """
    This subroutine takes a single file containing both the track and route information.
    This preserves ONLY the danger, food, and control waypoints.
    Personal use case: send route to Garmin via RideWithGPS and export from Garmin. Simpler but trims waypoint names.
    :param filename:
    :return:
    """
    original_gpx = read_gpx(filename)

    # keep danger waypoints
    danger_wps = get_waypoints_by_type(original_gpx, wp_type='DANGER')

    # keep food waypoints
    food_wps = get_waypoints_by_type(original_gpx, wp_type='FOOD')

    # keep controls
    reg_for_controls = 'Control'
    control_wps = get_waypoints(original_gpx, reg_for_controls)
    set_waypoint_point_type(control_wps, wp_type='Control')

    original_gpx.waypoints = danger_wps + food_wps + control_wps

    return original_gpx


def from_track_course_file(track_file: str, route_file: str):
    """
    This subroutine takes two filename: a track and route file.
    The track file contains only the points while the route contains only the cues/waypoints.
    Personal use case: export route and track directly from RideWithGPS in order to get untrimmed descriptions.
    :param track_file:
    :param route_file:
    :return:
    """
    track = read_gpx(track_file)
    route = read_gpx(route_file)

    # keep danger waypoints
    danger_wps = get_route_points_by_type(route, wp_type='Danger')

    # keep food waypoints
    food_wps = get_route_points_by_type(route, wp_type='Food')

    # keep controls
    control_wps = get_route_points_by_type(route, wp_type='Control', wp_type_override="Checkpoint")

    track.waypoints = danger_wps + food_wps + control_wps

    return track


def main():
    from_single = False

    if from_single:
        single_file = r"S:\Downloads\COURSE_340564128.gpx"
        gpx = from_single_file(single_file)
    else:
        track_file = r"S:\Downloads\Double_Eagles_400K_track.gpx"
        route_file = r"S:\Downloads\Double_Eagles_400K_route.gpx"
        gpx = from_track_course_file(track_file, route_file)

    save_gpx('T-Double_Eagles_400k.gpx', gpx)


if __name__ == '__main__':
    main()
