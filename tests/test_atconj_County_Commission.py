from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atconj_County_Commission import AtconjCountyCommissionSpider

test_response = file_response(
    join(dirname(__file__), "files", "atconj_County_Commission.html"),
    url="https://www.atlanticcountynj.gov/government/county-government/board-of-county-commissioners/meeting-schedule-agendas-and-minutes/-toggle-all",  # noqa
)
spider = AtconjCountyCommissionSpider()

freezer = freeze_time("2024-12-13")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Atlantic County Board of County Commissioners"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2025, 1, 7, 16, 0)


def test_end():
    assert parsed_items[0]["end"] == None


def test_time_notes():
    assert (
        parsed_items[0]["time_notes"]
        == "All Commissioner meetings held on First and Third Tuesdays at 4:00 pm unless otherwise noted."  # noqa
    )


def test_id():
    assert (
        parsed_items[0]["id"]
        == "atconj_County_Commission/202501071600/x/atlantic_county_board_of_county_commissioners"  # noqa
    )


def test_status():
    assert parsed_items[0]["status"] == "tentative"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Atlantic County Institute of Technology",
        "address": "Atlantic County Institute of Technology, 5080 Atlantic Avenue Mays Landing, New Jersey 08330",  # noqa
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.atlanticcountynj.gov/government/county-government/board-of-county-commissioners/meeting-schedule-agendas-and-minutes/-toggle-all"  # noqa
    )


def test_links():
    assert parsed_items[0]["links"] == []


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
