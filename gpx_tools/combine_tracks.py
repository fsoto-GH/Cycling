from gpx_tools.utils import read_gpx, save_gpx


def main():
    files = [r"S:\Downloads\to_two_eagles.gpx", r"W:\Python\EnduranceCalculations\Cycling\gpx_tools\T-Double_Eagles_400k.gpx" , r"S:\Downloads\home.gpx"]

    gpxs = [read_gpx(file) for file in files]

    for gpx in gpxs[1:]:
        for point in gpx.tracks[0].segments[0].points:
            gpxs[0].tracks[0].segments[0].points.append(point)

    save_gpx('combined_track.gpx', gpxs[0])


if __name__ == '__main__':
    main()
