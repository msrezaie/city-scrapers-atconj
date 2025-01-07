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
    assert parsed_items[3]["title"] == "Atlantic County Board of County Commissioners"


def test_description():
    assert parsed_items[3]["description"] == ""


def test_start():
    assert parsed_items[3]["start"] == datetime(2024, 11, 19, 16, 0)


def test_end():
    assert parsed_items[3]["end"] is None


def test_time_notes():
    assert (
        parsed_items[3]["time_notes"]
        == "All Commissioner meetings held on First and Third Tuesdays at 4:00 pm unless otherwise noted."  # noqa
    )


def test_id():
    assert (
        parsed_items[3]["id"]
        == "atconj_County_Commission/202411191600/x/atlantic_county_board_of_county_commissioners"  # noqa
    )


def test_status():
    assert parsed_items[3]["status"] == "passed"


def test_location():
    assert parsed_items[3]["location"] == {
        "name": "Stillwater Building",
        "address": "201 S. Shore Road Northfield, New Jersey 08225",
    }


def test_source():
    assert (
        parsed_items[3]["source"]
        == "https://www.atlanticcountynj.gov/government/county-government/board-of-county-commissioners/meeting-schedule-agendas-and-minutes/-toggle-all"  # noqa
    )


def test_links():
    assert parsed_items[3]["links"] == [
        {
            "href": "https://www.atlanticcountynj.gov/home/showpublisheddocument/22173/638672779908270000",  # noqa
            "title": "Agenda",
        },
        {
            "href": "https://www.atlanticcountynj.gov/home/showpublisheddocument/22235/638690116199730000",  # noqa
            "title": "Minutes",
        },
    ]


def test_classification():
    assert parsed_items[3]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
