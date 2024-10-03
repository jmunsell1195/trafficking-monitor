import logging
import os
import time

import bs4
import dotenv
import openai_models
from openai_models import gpt4_ncmec_formatter
from pymongo import MongoClient
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        NoSuchElementException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

dotenv.load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

mongo_client = MongoClient("mongodb://localhost:27017")
openai_client = client = openai_models.OpenAI(api_key=openai_api_key)

ncmec_data = mongo_client["ncmec_data"]
records = ncmec_data["records"]

search_url = "https://www.missingkids.org/gethelpnow/search"

html_pages = []


def get_html(search_url: str = search_url, n_pages: int = 20) -> None:
    global html_pages
    driver = webdriver.Chrome()
    driver.get(search_url)

    Select(driver.find_element(By.ID, "locationCountry")).select_by_visible_text(
        "United States"
    )

    driver.find_element(By.ID, "js-submit-form").click()

    html_pages.append(driver.page_source)

    for page in range(n_pages):
        try:
            driver.find_element(By.LINK_TEXT, ">").click()
            html_pages.append(driver.page_source)
            time.sleep(1.5)
            print(page)
        except NoSuchElementException:
            break
        except ElementClickInterceptedException:
            break

    driver.close()


def process_html() -> list:
    global html_pages
    all_page_images = []
    all_page_info = []
    for doc in html_pages:
        page_image_links = []
        page_missing_info = []
        soup = bs4.BeautifulSoup(doc, "html.parser")
        links = soup.find_all("a", class_="missing-person-link")
        for link in links:
            image = link.find("img")
            page_image_links.append(image["src"])

        info_div = soup.find_all("div", class_="missing-person-info")
        for div in info_div:
            page_missing_info.append(div)
        all_page_images.append(page_image_links)
        all_page_info.append(page_missing_info)

    return all_page_images, all_page_info


def scrape_ncmec():
    logging.info("Run Started")
    get_html(n_pages=250)
    logging.info("get_html completed")
    page_links, page_info = process_html()
    logging.info("process_html completed")
    missing_persons_lists = [
        gpt4_ncmec_formatter(page_image_links=images, page_info=info)
        for images, info in zip(page_links, page_info)
    ]
    logging.info("gpt-4 completed")
    missing_persons_lists = [
        eval(missing_persons.replace("```", "").strip("json"))
        for missing_persons in missing_persons_lists
    ]
    logging.info("reformatting finished")
    for missing_persons_list in missing_persons_lists:
        records.insert_many(missing_persons_list)
    logging.info("records put in mongo")


if __name__ == "__main__":
    scrape_ncmec()
