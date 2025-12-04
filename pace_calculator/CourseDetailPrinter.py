import math
from dataclasses import dataclass
from datetime import datetime, timedelta

import logging

from Cycling.pace_calculator.CourseDetail import CourseDetail
from Cycling.pace_calculator.PrinterField import PrinterField
from Cycling.pace_calculator.SplitDetail import SplitDetail
from Cycling.pace_calculator.Utils import hours_to_pretty, span_to_pretty

logging.basicConfig(level=logging.DEBUG)


@dataclass
class CourseDetailPrinter:
    course_details: CourseDetail
    keys_to_exclude: set[str] = None
    keys_to_rename: dict[str: str] = None
    SPACER = ' │ '

    FIELD_PROPS = {
        'distance': PrinterField(
            name="Distance",
            header_format=">8s",
            value_format='8.2f',
            width=8
        ),
        'span': PrinterField(
            name=f"{'Start':>7s}, {'End':>7s}",
            header_format=">16s",
            value_format='16s',
            value_transformer=span_to_pretty,
            width=16
        ),
        'moving_speed': PrinterField(
            name="Moving Speed",
            header_format=">12s",
            value_format='12.2f',
            width=12
        ),
        'moving_time': PrinterField(
            name="Moving Time",
            header_format=">19s",
            value_format='19s',
            value_transformer=hours_to_pretty,
            width=19
        ),
        'down_time': PrinterField(
            name="Down Time",
            header_format=">19s",
            value_format='19s',
            value_transformer=hours_to_pretty,
            width=19
        ),
        'pace': PrinterField(
            name="Pace",
            header_format=">6s",
            value_format='6.2f',
            width=6
        ),
        'start_time': PrinterField(
            name="Start Time",
            header_format=">17s",
            value_format='%m/%d %I:%M:%S %p',
            width=17
        ),
        'split_time': PrinterField(
            name="Split Time",
            header_format=">19s",
            value_format='19s',
            value_transformer=hours_to_pretty,
            width=19
        ),
        'adjustment_time': PrinterField(
            name="Adjustment Time",
            header_format=">19s",
            value_format='19s',
            value_transformer=hours_to_pretty,
            width=19
        ),
        'adjustment_start': PrinterField(
            name="Adjustment Start",
            header_format=">17s",
            value_format='%m/%d %I:%M:%S %p',
            width=17
        ),
        'total_time': PrinterField(
            name="Total Time",
            header_format=">19s",
            value_format='19s',
            value_transformer=hours_to_pretty,
            width=19
        ),
        'end_time': PrinterField(
            name="End Time",
            header_format=">17s",
            value_format='%m/%d %I:%M:%S %p',
            width=17
        ),
    }

    REST_STOP_HEADERS = {
        'name': PrinterField(
            name="Rest Stop Name",
            header_format="<20s",
            value_format='<20s',
            width=20
        ),
        'hours': PrinterField(
            name="Rest Stop Hours",
            header_format="<15s",
            value_format='>15s',
            width=15
        ),
        'address': PrinterField(
            name="Rest Stop Address",
            header_format=">40s",
            value_format='>40s',
            width=40
        ),
        'alt': PrinterField(
            name="Alternate URL",
            header_format="<50s",
            value_format='<50s',
            width=50
        )
    }

    def print(self, include_sub_splits: bool = False, include_stops: bool = True):
        segment_details = self.course_details.segment_details

        field_keys_showing = self.__exposed_fields(include_stops)
        dash_count = self.__compute_dash_count(field_keys_showing, include_stops)

        for segment_detail in segment_details:
            self.__print_header(field_keys_showing)
            print('─' * dash_count)

            for split in segment_detail.split_details:
                self.__print_detail(split, field_keys_showing, include_sub_splits)

            print('─' * dash_count)

        # print('─' * dash_count)
        # self.__print_footer(summary,
        #                     field_keys_showing)
        #
        # print(f"{'Total Distance':14}: {summary['distance']:>8.3f}")
        # print(f"{'Time Span':14}: {summary['start_time']:%m/%d %I:%M %p} - {summary['end_time']:%m/%d %I:%M %p}")
        # print(f"{'Moving Time':14}: {hours_to_pretty(summary['moving_time']).strip():14} "
        #       f"[{summary['moving_time'].total_seconds() / 3600:7.3f} hours]")
        # print(f"{'Down Time':14}: {hours_to_pretty(summary['down_time']).strip():14} "
        #       f"[{summary['down_time'].total_seconds() / 3600:7.3f} hours]")
        # print(f"{'Adj. Time':14}: {hours_to_pretty(summary['adjustment_time']).strip():14} "
        #       f"[{summary['adjustment_time'].total_seconds() / 3600:7.3f} hours]")
        # # print(f"{'Moving + Down':14}: {hrs_prty(summary['moving_time'] + summary['down_time']).strip():14} "
        # #       f"[{(summary['moving_time'] + summary['down_time']).total_seconds() / 3600:7.3f} hours]")
        # print(f"{'Elapsed Time':14}: {hours_to_pretty(summary['total_time']).strip():14} "
        #       f"[{summary['total_time'].total_seconds() / 3600:7.3f} hours]")
        # print(f"{'Pace':14}: {summary['distance'] / (summary['total_time'].total_seconds() / 3600):>8.3f}")
        # print(
        #     f"{'Distance/Day':14}: {summary['distance'] / (summary['total_time'].total_seconds() / (3600 * 24)):>8.3f}")
        # print(f"{'Moving/Elapsed':14}: {(summary['moving_time'] / summary['total_time']):>8.3%}")
        # print(f"{'Down/Elapsed':14}: {summary['down_time'] / summary['total_time']:>8.3%}")
        # print(f"{'Adj./Elapsed':14}: {summary['adjustment_time'] / summary['total_time']:>8.3%}")
        # print(f"{'Down/Moving':14}: {summary['down_time'] / summary['moving_time']:>8.3%}")
        # print(f"{'Adj./Moving':14}: {summary['adjustment_time'] / summary['moving_time']:>8.3%}")

    def __exposed_fields(self, include_stop_info):
        if self.keys_to_rename is None:
            self.keys_to_rename = {}

        if self.keys_to_exclude is None:
            self.keys_to_exclude = set()

        field_keys_showing = set(self.FIELD_PROPS.keys())
        if include_stop_info:
            field_keys_showing |= set(self.REST_STOP_HEADERS.keys())

        field_keys_showing -= self.keys_to_exclude

        return field_keys_showing

    def __print_header(self, field_keys_showing: set[str]):
        res = []
        for _k in self.FIELD_PROPS:
            if _k in field_keys_showing:
                header_override = self.keys_to_rename.get(_k, None)
                res.append(self.FIELD_PROPS[_k].formatted_header(header_override))

        for _k in self.REST_STOP_HEADERS:
            if _k in field_keys_showing:
                header_override = self.keys_to_rename.get(_k, None)
                res.append(self.REST_STOP_HEADERS[_k].formatted_header(header_override))

        print(self.SPACER.join(res))

    def __print_detail(self, split: SplitDetail, field_keys_showing: set[str], is_sub_split: bool = False):
        res = []
        for _k in self.FIELD_PROPS:
            if _k in field_keys_showing:
                _v = self.FIELD_PROPS[_k].formatted_value(split.__getattribute__(_k))
                res.append(_v)

        for _k in self.REST_STOP_HEADERS:
            if _k in field_keys_showing:
                if split.rest_stop is None:
                    _v = self.REST_STOP_HEADERS[_k].formatted_value()
                else:
                    _v = self.REST_STOP_HEADERS[_k].formatted_value(split.rest_stop.__getattribute__(_k))
                res.append(_v)
        print(f'{self.SPACER.join(res)}' if is_sub_split else self.SPACER.join(res))

    def __print_footer(self, summary: dict[str: [str | float | datetime]], keys_to_include: set[str]):
        ...
        # res = []
        # for key in self.FIELD_PROPS:
        #     if key not in summary:
        #         logging.error(f"The key: '{key}' does not exist in split summary.")
        #
        #     if key in keys_to_include and key in summary:
        #         val = summary[key]
        #         is_filler = type(val) == str and set(val) == {'-'}
        #         if 'transformer' in self.FIELD_PROPS[key] and not is_filler:
        #             res.append(self.FIELD_PROPS[key]['transformer'](summary[key]))
        #         elif is_filler:
        #             res.append(format_field(val=val, formatting=self.FIELD_PROPS[key]['header_formatting']))
        #         elif val is None:
        #             res.append(f'{"":{self.FIELD_PROPS[key]["width"]}}')
        #         else:
        #             res.append(format_field(val=val, formatting=self.FIELD_PROPS[key]['value_formatting']))
        #
        # print(self.SPACER.join(res))

    def __compute_dash_count(self, field_keys_showing: set[str], include_stop_info: bool):
        spacers_spacing = len(self.SPACER) * (len(field_keys_showing) - 1)
        base_headers = sum(self.FIELD_PROPS[_k].width for _k in self.FIELD_PROPS if _k in field_keys_showing)
        stops_width = sum(self.REST_STOP_HEADERS[_k].width for _k in self.REST_STOP_HEADERS if _k in field_keys_showing)
        return base_headers + spacers_spacing + (stops_width if include_stop_info else 0)
