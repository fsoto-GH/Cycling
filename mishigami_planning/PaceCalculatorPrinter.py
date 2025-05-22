from datetime import datetime, timedelta

from mishigami_planning.PaceCalculator import PaceCalculator
from mishigami_planning.Split import Split, RestStop
from mishigami_planning.Utils import format_field, hours_to_pretty

from Utils import hours_to_pretty as hrs_prty

import logging

logging.basicConfig(level=logging.DEBUG)


class PaceCalculatorPrinter:
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
            "header_formatting": ">19s",
            "value_formatting": '19s',
            "transformer": hours_to_pretty,
            "width": 19
        },
        'down_time': {
            "name": "Down Time",
            "header_formatting": ">19s",
            "value_formatting": '19s',
            "transformer": hours_to_pretty,
            "width": 19
        },
        'split_speed': {
            "name": "Split Speed",
            "header_formatting": ">11s",
            "value_formatting": '11.2f',
            "width": 11
        },
        'pace': {
            "name": "Pace",
            "header_formatting": ">6s",
            "value_formatting": '6.2f',
            "width": 6
        },
        'start_time': {
            "name": "Start Time",
            "header_formatting": ">17s",
            "value_formatting": '%m/%d %I:%M:%S %p',
            "width": 17
        },
        'split_time': {
            "name": "Split Time",
            "header_formatting": ">19s",
            "value_formatting": '19s',
            "transformer": hours_to_pretty,
            "width": 19
        },
        'adjustment_time': {
            "name": "Adjustment Time",
            "header_formatting": ">19s",
            "value_formatting": '19s',
            "transformer": hours_to_pretty,
            "width": 19
        },
        'adjustment_start': {
            "name": "Adjustment Start",
            "header_formatting": ">17s",
            "value_formatting": '%m/%d %I:%M:%S %p',
            "width": 17
        },
        'total_time': {
            "name": "Total Time",
            "header_formatting": ">19s",
            "value_formatting": '19s',
            "transformer": hours_to_pretty,
            "width": 19
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
        'rest_stop_alt': {
            "name": "Alternate URL",
            "header_formatting": "<50s",
            "value_formatting": '<50s',
            "width": 50
        },
    }
    SPACER = ' │ '

    def __init__(self,
                 pace_calculator: PaceCalculator,
                 keys_to_exclude: set[str] = None,
                 keys_to_rename: dict[str: str] = None):
        """

        :param pace_calculator:
        :param keys_to_exclude: fields by key to remove from printing
        :param keys_to_rename: a dictionary containing fields by key to rename
        """
        self.pace_calculator = pace_calculator
        self.keys_to_exclude = keys_to_exclude
        self.keys_to_rename = keys_to_rename

    def print(self, with_sub_splits: bool = False):
        splits, summary = self.pace_calculator.get_split_breakdown()
        include_stops = any('stop' in split_detail for split_detail in splits)
        field_keys_showing = self.__exposed_fields(include_stops)

        dash_count = self.__compute_dash_count(field_keys_showing, include_stops)

        self.__print_header(field_keys_showing)
        print('─' * dash_count)

        for split_detail_line in splits:
            show_sub_splits = 'sub_splits' in split_detail_line and with_sub_splits
            if show_sub_splits:
                for sub_split in split_detail_line['sub_splits']:
                    self.__print_detail(sub_split, field_keys_showing, is_sub_split=True)
            print(('▄' if show_sub_splits else '¨') * dash_count)
            self.__print_detail(split_detail_line,
                                field_keys_showing)
            print(('▀' if show_sub_splits else '¨') * dash_count)

        print('─' * dash_count)
        self.__print_footer(summary,
                            field_keys_showing)

        print(f"{'Total Distance':14}: {summary['distance']:>8.3f}")
        print(f"{'Time Span':14}: {summary['start_time']:%m/%d %I:%M %p} - {summary['end_time']:%m/%d %I:%M %p}")
        print(f"{'Moving Time':14}: {hrs_prty(summary['moving_time']).strip():14} "
              f"[{summary['moving_time'].total_seconds() / 3600:7.3f} hours]")
        print(f"{'Down Time':14}: {hrs_prty(summary['down_time']).strip():14} "
              f"[{summary['down_time'].total_seconds() / 3600:7.3f} hours]")
        print(f"{'Adj. Time':14}: {hrs_prty(summary['adjustment_time']).strip():14} "
              f"[{summary['adjustment_time'].total_seconds() / 3600:7.3f} hours]")
        # print(f"{'Moving + Down':14}: {hrs_prty(summary['moving_time'] + summary['down_time']).strip():14} "
        #       f"[{(summary['moving_time'] + summary['down_time']).total_seconds() / 3600:7.3f} hours]")
        print(f"{'Elapsed Time':14}: {hrs_prty(summary['total_time']).strip():14} "
              f"[{summary['total_time'].total_seconds() / 3600:7.3f} hours]")
        print(f"{'Pace':14}: {summary['distance'] / (summary['total_time'].total_seconds() / 3600):>8.3f}")
        print(
            f"{'Distance/Day':14}: {summary['distance'] / (summary['total_time'].total_seconds() / (3600 * 24)):>8.3f}")
        print(f"{'Moving/Elapsed':14}: {(summary['moving_time'] / summary['total_time']):>8.3%}")
        print(f"{'Down/Elapsed':14}: {summary['down_time'] / summary['total_time']:>8.3%}")
        print(f"{'Adj./Elapsed':14}: {summary['adjustment_time'] / summary['total_time']:>8.3%}")
        print(f"{'Down/Moving':14}: {summary['down_time'] / summary['moving_time']:>8.3%}")
        print(f"{'Adj./Moving':14}: {summary['adjustment_time'] / summary['moving_time']:>8.3%}")

    def __exposed_fields(self, include_stop_info):
        if self.keys_to_rename is None:
            self.keys_to_rename = {}

        if self.keys_to_exclude is None:
            self.keys_to_exclude = set()

        field_keys_showing = set(self.FIELD_PROPS.keys())
        if include_stop_info:
            field_keys_showing |= set(self.LOCATION_HEADERS.keys())

        field_keys_showing -= self.keys_to_exclude

        return field_keys_showing

    def __print_header(self, field_keys_showing: set[str]):
        res = [format_field(val=_v['name'] if _k not in self.keys_to_rename else self.keys_to_rename[_k][:_v['width']],
                            formatting=f"{_v['header_formatting']}")
               for _k, _v in self.FIELD_PROPS.items() if _k in field_keys_showing]

        res_2 = [
            format_field(val=_v['name'] if _k not in self.keys_to_rename else self.keys_to_rename[_k][:_v['width']],
                         formatting=f"{_v['header_formatting']}")
            for _k, _v in self.LOCATION_HEADERS.items() if _k in field_keys_showing]
        print(self.SPACER.join(res + res_2))

    def __print_detail(self,
                       split: dict[str, any],
                       field_keys_showing: set[str],
                       is_sub_split: bool = False):
        res = []
        for key in self.FIELD_PROPS:
            if key not in split:
                logging.error(f"The key: '{key}' does not exist in split detail.")
            if key in field_keys_showing and key in split:
                _v = split[key]
                if 'transformer' in self.FIELD_PROPS[key]:
                    _v = self.FIELD_PROPS[key]['transformer'](split[key])

                res.append(format_field(val=_v, formatting=self.FIELD_PROPS[key]['value_formatting']))

        for key in self.LOCATION_HEADERS:
            if key in field_keys_showing:
                _v = ''
                # this is not very readable, but it essentially looks
                # at the LOCATION_HEADERS keys' last word and searches for it in the split's stop location
                # ex: 'name' maps to split['stop']['rest_stop_name'] '
                # ex2: 'address' maps to split['stop']['rest_stop_address']
                # known issue: rest_stop_* can coincide; like, 'hours' for 'rest_stop_hours' | 'rest_stop_laundry_hours'
                stop: RestStop = split['stop']
                if stop and (_k := key.split('_')[-1]) in stop.__dict__:
                    _v = stop.__getattribute__(_k) or ''

                    if _k == 'hours':
                        d: datetime = split['end_time']
                        _v = _v[d.weekday()]
                        res.append(format_field(val=_v[:15], formatting=self.LOCATION_HEADERS[key]['value_formatting']))
                    else:
                        res.append(format_field(val=_v[:self.LOCATION_HEADERS[key]['width']],
                                                formatting=self.LOCATION_HEADERS[key]['value_formatting']))
                else:
                    res.append(format_field(val='',
                                            formatting=self.LOCATION_HEADERS[key]['value_formatting']))

        print(f'{self.SPACER.join(res)}' if is_sub_split else self.SPACER.join(res))

    def __print_footer(self, summary: dict[str: [str | float | datetime]], keys_to_include: set[str]):
        res = []
        for key in self.FIELD_PROPS:
            if key not in summary:
                logging.error(f"The key: '{key}' does not exist in split summary.")

            if key in keys_to_include and key in summary:
                val = summary[key]
                is_filler = type(val) == str and set(val) == {'-'}
                if 'transformer' in self.FIELD_PROPS[key] and not is_filler:
                    res.append(self.FIELD_PROPS[key]['transformer'](summary[key]))
                elif is_filler:
                    res.append(format_field(val=val, formatting=self.FIELD_PROPS[key]['header_formatting']))
                elif val is None:
                    res.append(f'{"":{self.FIELD_PROPS[key]["width"]}}')
                else:
                    res.append(format_field(val=val, formatting=self.FIELD_PROPS[key]['value_formatting']))

        print(self.SPACER.join(res))

    def __compute_dash_count(self, field_keys_showing: set[str], include_stop_info: bool):
        w = 'width'
        spacers_spacing = len(self.SPACER) * (len(field_keys_showing) - 1)
        base_headers = sum(self.FIELD_PROPS[k][w] for k in field_keys_showing if k in self.FIELD_PROPS)
        location_headers = sum(self.LOCATION_HEADERS[k][w] for k in field_keys_showing if k in self.LOCATION_HEADERS)
        return base_headers + spacers_spacing + (location_headers if include_stop_info else 0)


def main():
    initial_mph = 17.2
    min_mph = 16.8
    decay_per_split_mph = 0.2
    downtime_ratio = 0.05

    distances = [Split(distance=571.5, adjustment_time=timedelta(hours=9)), Split(distance=549.7)]

    start_date = datetime(year=2025, month=7, day=12, hour=6, minute=0)

    pace_calculator = PaceCalculator()
    pace_calculator.set_split_info(
        splits=distances,
        start_moving_speed=initial_mph,
        min_moving_speed=min_mph,
        decay_per_split=decay_per_split_mph,
        start_time=start_date,
        downtime_ratio=downtime_ratio,
        sub_split_distances=100
    )

    printer = PaceCalculatorPrinter(pace_calculator)
    printer.print(with_sub_splits=False)


if __name__ == '__main__':
    main()
