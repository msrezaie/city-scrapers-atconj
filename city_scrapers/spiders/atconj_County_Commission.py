import json

import scrapy
from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as dateparse
from scrapy import Selector


class AtconjCountyCommissionSpider(CityScrapersSpider):
    name = "atconj_County_Commission"
    agency = "Atlantic County Board of County Commissioners"
    timezone = "America/New_York"

    original_url = "https://www.atlanticcountynj.gov"
    meetings_url = "https://www.atlanticcountynj.gov/government/county-government/board-of-county-commissioners/meeting-schedule-agendas-and-minutes/-toggle-all"  # noqa

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
    }

    default_location = {
        "name": "Stillwater Building",
        "address": "Stillwater Building, 201 S. Shore Road Northfield, New Jersey 08225",  # noqa
    }

    """
    This website would return a 403 error if the request
    is made with the default headers. The headers below
    are the ones that are needed to make the request.
    """

    def start_requests(self):
        headers = {
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",  # noqa
        }

        yield scrapy.Request(
            url=self.meetings_url, headers=headers, callback=self.parse
        )

    def parse(self, response):
        rows = response.css("table.front_end_widget tbody tr").getall()
        scripts = response.css("table.front_end_widget tbody script::text").getall()
        time_note = response.css("div#widget_45_2122_758 p::text").get()

        for row_item, script_item in zip(rows, scripts):
            content = json.loads(script_item)

            meeting = Meeting(
                title="Atlantic County Board of County Commissioners",
                description="",
                classification=BOARD,
                start=self._parse_start(content),
                end=self._parse_end(content),
                all_day=False,
                time_notes=time_note.strip(),
                location=self._parse_location(content),
                links=self._parse_links(row_item),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return dateparse(item["startDate"]).astimezone(tz=None).replace(tzinfo=None)

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object."""
        return dateparse(item["endDate"]).astimezone(tz=None).replace(tzinfo=None)

    def _parse_location(self, item):
        location = item.get("location")
        if not location.get("address") or not location.get("name"):
            return self.default_location
        return {"name": location.get("name"), "address": location.get("address")}

    def _parse_links(self, item):
        links = []

        item = Selector(text=item)
        agenda_url = item.css("td.event_agenda a").get()
        minutes_url = item.css("td.event_minutes a").get()
        if agenda_url:
            agenda_url = agenda_url.split('href="')[1].split('"')[0]
            links.append({"href": self.original_url + agenda_url, "title": "Agenda"})
        if minutes_url:
            minutes_url = minutes_url.split('href="')[1].split('"')[0]
            links.append({"href": self.original_url + minutes_url, "title": "Minutes"})
        return links
