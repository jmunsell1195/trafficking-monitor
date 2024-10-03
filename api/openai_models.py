import os

import dotenv
from openai import OpenAI
from prompts import (adult_ad_scraper_system, ncmec_formatter_prompt,
                     ncmec_formatter_system, topic_main_page_scraper_system, trafficking_ad_system)
from utils import output_formatting

dotenv.load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = client = OpenAI(api_key=openai_api_key)


page_cnt = 0


def gpt4_ncmec_formatter(page_info, page_image_links, client=openai_client):
    global page_cnt
    print(f"processing page: {page_cnt}")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        messages=[
            {"role": "system", "content": ncmec_formatter_system},
            {
                "role": "user",
                "content": ncmec_formatter_prompt(
                    html=page_info, link=page_image_links
                ),
            },
        ],
    )
    page_cnt += 1

    output = response.choices[0].message.content
    try:
        return eval(output_formatting(output))
    except Exception as e:
        print(f"parsing failed on page: {page_cnt}")
        print(output)
        return []


def gpt4_main_page_scraper(page_html, system=topic_main_page_scraper_system):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"```html: {page_html}```"},
        ],
    )
    output = response.choices[0].message.content
    try:
        return eval(output_formatting(output))
    except Exception as e:
        print(f"parsing failed: {output}")
        return []


def gpt4_ad_scraper(user, system=adult_ad_scraper_system, client=client):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    output = response.choices[0].message.content
    try:
        return eval(output_formatting(output))
    except Exception as e:
        print(f"parsing failed: {output}")
        return []


def gpt4_trafficking_keywords(user, system=trafficking_ad_system(), client=client):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    try:
        output = response.choices[0].message.content
        return eval(output)
    except Exception as e:
        return f"System error: {e}"
