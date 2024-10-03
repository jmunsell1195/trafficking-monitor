import requests
from openai_models import gpt4_ad_scraper, gpt4_main_page_scraper
from prompts import (ad_scraper_user, get_page_text, main_page_scraper_system,
                     top_most_page_scraper_system)
from pymongo import MongoClient
from utils import batch_html_pages

base_url = "https://www.2backpage.com/"
client = MongoClient("mongodb://localhost:27017")
db = client["backpageTexas"]
collection = db["sanAntonio"]


def is_adult(service: str) -> bool:
    return "adult" in service


def backpage_page_scraper(page_url: str) -> list[list[dict]]:
    page = requests.get(page_url).text
    print("***getting links to ads***\n")
    links = gpt4_main_page_scraper(page_html=page)
    print("***getting ad***\n")
    page_text = get_page_text(links)
    print("***getting batches***\n")
    batches = batch_html_pages(page_text, n_html_batch=3)
    print("***making user prompts***\n")
    user_prompts = ad_scraper_user(batches)
    print("***parsing ads***\n")
    post_details = [gpt4_ad_scraper(user_prompt) for user_prompt in user_prompts]
    return post_details


def scrape_by_state(
    state: str = "texas", city: str = "san-antonio", num_pages_to_scrape: int = 10
) -> None:
    front_page_html = requests.get(base_url).text
    cities_list_for_state = gpt4_main_page_scraper(
        page_html=front_page_html, system=top_most_page_scraper_system(state=state)
    )
    city_url = cities_list_for_state[city]
    city_main_html = requests.get(city_url).text
    services = gpt4_main_page_scraper(
        page_html=city_main_html, system=main_page_scraper_system
    )["services"]
    service_url = list(filter(is_adult, services))[0]
    print(service_url)
    for page in range(num_pages_to_scrape - 1):
        print(f"running page: {page}")
        if page:
            page_url = f"{service_url}/{150*(page+1)}"
            print(page_url)
            page_details = backpage_page_scraper(page_url=page_url)
            # commit to db
        else:
            print("front page")
            page_details = backpage_page_scraper(page_url=service_url)
