import os
from bs4 import PageElement, Tag
from ics import Calendar, Event
from datetime import datetime
import requests
import bs4
import pytz
import uuid


def generate_ics(events: list[dict]):
    calendar = Calendar()
    local_tz = pytz.timezone("America/Chicago")

    for event in events:
        e = Event()
        e.name = event["name"]
        e.begin = local_tz.localize(event["date"])
        e.location = event["location"]
        e.description = event['description']
        e.duration = {"days": 1}
        e.uid = event["uid"]

        calendar.events.add(e)

    return calendar


def scrape_events():
    """
    Scrapes events from the ChicagoRando website.
    Generates a UID from the name and date.
    :return:
    """
    domain = 'https://www.chicagorando.org'
    url = f"{domain}/schedule"

    response = requests.get(url)
    res = []

    if response.status_code == 200:
        _doc = bs4.BeautifulSoup(response.content, 'html.parser')
        events = _doc.select('#sections > section .content > div > div > div:nth-child(n+3)')

        for e in events:
            _elements = e.select_one('#sections > section .content > div > div > div:nth-child(n+3) > div > div > div')
            x: list[Tag | PageElement] = [e for e in _elements.children]
            _date_el: Tag = safe_index(x, 1)
            _dist, _loc, _name = extract_dist_loc(x, 2)
            _reg_link = extract_reg_link(x, 3, domain)

            _date = datetime.strptime(_date_el.text.strip(), '%B %d, %Y')
            _e_name = f"{_name}" if (_dist_str := regex_dist(_dist)) is None else f"{_dist_str.lower()}: {_name}"

            res.append({
                'location': _loc,
                'date': _date,
                'name': _e_name,
                'description': f"{_dist}\n{_loc}\n{'URL: '}{url}\n{'LINK: '}{_reg_link}",
                'uid': f"{uuid.uuid5(uuid.NAMESPACE_DNS, f'{_name}|{_date}')}"
            })

    return res


def extract_reg_link(x, i, url_prefix=""):
    if (link_container := safe_index(x, i)) is not None and not link_container.string.isspace():
        _reg_link = link_container.select_one('a')['href']
    else:
        _reg_link = 'TBD'

    if _reg_link.startswith("/"):
        return url_prefix + _reg_link

    return _reg_link


def extract_dist_loc(x, i):
    _dist_loc_el = safe_index(x, i)

    if (_name := get_text(_dist_loc_el, 'strong')) is not None:
        _dist = _dist_loc_el.contents[-3].text
        _loc = _dist_loc_el.contents[-1].text
    else:
        _dist = _dist_loc_el.contents[0].text
        _loc = 'TBD'
        _name = 'TBD'

    return _dist.strip(), _loc.strip(), _name.strip()


def safe_index(x, i):
    try:
        return x[i]
    except IndexError as _:
        return None


def regex_dist(txt: str):
    import re
    res = re.search(r'\d+\s?(km|mi)', txt, re.IGNORECASE)

    if res:
        return res.group(0)


def get_text(elem, selector: str, default: str = None):
    if (x := elem.select_one(selector)) is not None:
        return x.text
    return None


def save_ics(calendar: Calendar, filename: str):
    with open(filename, "w") as f:
        f.writelines(calendar)
    print(f"ICS file generated: {filename}")


def main():
    """
    This does a bit of web-scraping on the ChiRand website to gather the schedule and some details, and it saves them
    in a file named events_yyyy_mm_dd.ics
    This involves the date, distance, name, and link to registration if it exists.

    :return:
    """
    events = scrape_events()
    ics_calendar = generate_ics(events)
    save_ics(ics_calendar, filename=f"events_{datetime.today():%Y_%m_%d}.ics")


if __name__ == '__main__':
    main()
