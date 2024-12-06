import json
from datetime import datetime
from urllib.parse import urljoin

import scrapy
from city_scrapers_core.constants import (
    CANCELLED,
    CITY_COUNCIL,
    CLASSIFICATIONS,
    NOT_CLASSIFIED,
    PASSED,
    TENTATIVE,
)
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class AtlanticCitySpider(CityScrapersSpider):
    name = "atconj_Atlantic_City"
    agency = "Atlantic City"
    timezone = "America/New_York"

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
    }

    """
    The website layout of this agency uses JavaScript to dynamically
    load meetings for one month at a time, making it challenging to
    scrape data directly from the HTML/CSS structure of the site.

    So instead API endpoints from the agency's URL are used to fetch
    the meetings data:
    - `meetings_url`: provides a list of all meetings for a given time
    period.
    - `meeting_detail_url`: retrieves detailed information for each
    meeting using its ID.

    Additionally, a third url `calender_source` is used as the source
    field of the meeting since it is more user friendly to navigate
    than the api endpoints.
    """
    meetings_url = "https://www.acnj.gov/api/data/GetCalendarMeetings?end=06%2F30%2F2025+12:00+am&meetingTypeID=all&start=06%2F01%2F2024+12:00+am"  # noqa
    meeting_detail_url = "https://www.acnj.gov/api/data/GetMeeting?id="
    calender_source = "https://www.acnj.gov/calendar"

    def start_requests(self):
        yield scrapy.Request(url=self.meetings_url, method="GET", callback=self.parse)

    def parse(self, response):
        data = json.loads(response.text)
        for item in data:
            meeting_id = item["id"]
            meeting_detail_url = self.meeting_detail_url + meeting_id

            yield scrapy.Request(
                url=meeting_detail_url,
                method="GET",
                callback=self.parse_meeting,
                cb_kwargs={"item": item},
            )

    def parse_meeting(self, response, item):
        meeting_detail = json.loads(response.text)

        meeting = Meeting(
            title=item["title"],
            description="",
            classification=self._parse_classification(meeting_detail),
            start=parse(item["start"]),
            end=None,
            all_day=item["allDay"],
            time_notes="",
            location=self._parse_location(meeting_detail),
            links=self._parse_links(meeting_detail),
            source=self.calender_source,
        )

        meeting["status"] = self._get_status(meeting_detail)
        meeting["id"] = int(item["id"])

        yield meeting

    def _parse_classification(self, item):
        for classification in CLASSIFICATIONS:
            if classification.lower() in item["Meeting_Type"].lower():
                return classification
            elif "council" in item["Meeting_Type"].lower():
                return CITY_COUNCIL
        return NOT_CLASSIFIED

    def _parse_location(self, item):
        meeting_location = (
            item["Meeting_Location"]
            or "1301 Bacharach Boulevard Atlantic City, NJ, 08401"
        )

        if "-" in meeting_location:
            return {
                "address": meeting_location.split("-")[1].strip(),
                "name": meeting_location.split("-")[0].strip(),
            }
        else:
            return {
                "address": meeting_location,
                "name": "City Hall of Atlantic City",
            }

    def _parse_links(self, item):
        base_url = "https://www.acnj.gov/"
        keys = ["Meeting_AgendaPDF", "Meeting_MinutesPDF", "Meeting_NoticePDF"]
        titles = ["Agenda", "Minutes", "Notice"]

        links = [
            {"title": title, "href": urljoin(base_url, item.get(key, ""))}
            for title, key in zip(titles, keys)
            if item.get(key)
        ]
        return links

    def _get_status(self, item):
        if item["Meeting_IsCanceled"]:
            return CANCELLED
        if parse(item["Meeting_DateTime"]) < datetime.now():
            return PASSED
        return TENTATIVE
