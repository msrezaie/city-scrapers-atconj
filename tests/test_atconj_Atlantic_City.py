from datetime import datetime
from os.path import dirname, join

import scrapy
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atconj_Atlantic_City import AtlanticCitySpider

test_response = file_response(
    join(dirname(__file__), "files", "atconj_Atlantic_City.json"),
    url="https://www.acnj.gov/api/data/GetCalendarMeetings?end=06%2F30%2F2025+12:00+am&meetingTypeID=all&start=06%2F01%2F2024+12:00+am",  # noqa
)

meeting_detail_response = file_response(
    join(dirname(__file__), "files", "atconj_Atlantic_City_meeting_detail.json"),
    url="https://www.acnj.gov/api/data/GetMeeting?id=429",
)

spider = AtlanticCitySpider()

freezer = freeze_time("2024-12-06")
freezer.start()

parsed_items = []
for req in spider.parse(test_response):
    if isinstance(req, scrapy.Request):
        meeting_detail_item = spider.parse_meeting(
            meeting_detail_response, req.cb_kwargs["item"]
        )
        parsed_items.extend(meeting_detail_item)

freezer.stop()


def test_count():
    assert len(parsed_items) == 42


def test_title():
    assert parsed_items[0]["title"] == "CITISTAT Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 6, 26, 17, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_all_day():
    assert parsed_items[0]["all_day"] is False


def test_id():
    assert parsed_items[0]["id"] == 429


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "John F. Scarpa Academic Center",
        "address": "3711 Atlantic Ave., Atlantic City, NJ 08401",
    }


def test_source():
    assert parsed_items[0]["source"] == "https://www.acnj.gov/calendar"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.acnj.gov/_Content/pdf/agendas/2024-06-26-CITISTAT-Presentations.pdf",  # noqa
            "title": "Agenda",
        },
        {
            "href": "https://www.acnj.gov/_Content/pdf/minutes/2024-06-26-CITISTAT-Responses.pdf",  # noqa
            "title": "Minutes",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == NOT_CLASSIFIED
