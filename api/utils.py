import re
from io import BytesIO
from typing import Callable

import numpy as np
import requests
from bs4 import BeautifulSoup
from numpy import ndarray
from PIL import Image
from requests import Response
from skimage.transform import resize


def output_formatting(output: str) -> str:
    output = (
        output.replace("```", "").strip("json").replace("null", "None").strip("python")
    )
    return output


def get_backpage_ad_aoi(ad: str) -> str:
    soup = BeautifulSoup(ad, "html.parser")
    area_of_interest = str(soup.find("div", id="pageBackground"))
    return area_of_interest


def get_page_text(
    urls_list: list[str], post_process: Callable = get_backpage_ad_aoi
) -> list[str]:
    page_source_html_list = [post_process(requests.get(url).text) for url in urls_list]
    return page_source_html_list


def batch_html_pages(html_pages: list[str], n_html_batch: int = 5):
    page_source_html_list = html_pages
    length = len(page_source_html_list)
    html_pages = [
        page_source_html_list[n : n + n_html_batch + 1]
        for n in range(0, length, n_html_batch)
    ]
    return html_pages


def get_np_image(response):
    image = Image.open(BytesIO(response.content))
    image_np = np.array(image)
    return image_np


def get_cities_dict(links: list):
    pattern = r"https://([^.]+)\.2backpage\.com"
    city_dict = {}
    for city in links["cities"]:
        match = re.search(pattern, city)
        if match:
            city_name = match.group(1)
            service_urls = [
                url.replace("san-antonio", city_name) for url in links["services"]
            ]
            city_dict[city_name] = {"backpageUrl": city, "services": service_urls}
        else:
            print("No match found")
    return city_dict


us_states = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
]

us_states = [state.lower() for state in us_states]

trafficking_keywords = [
    "new in town",
    "young",
    "fresh",
    "innocent",
    "no limits",
    "no restrictions",
    "discreet",
    "24/7",
    "available now",
    "party",
    "fun",
    "ready",
    "VIP",
    "full service",
    "GFE",
]
