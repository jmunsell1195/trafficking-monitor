import requests
from utils import batch_html_pages, get_page_text, trafficking_keywords

## System Prompts
ncmec_formatter_system = """You will be shown some html with postings for up to 20 missing children. For each child, I want: 
    * A link to the child's photo: It will be a webaddress starting with 'https://api.missingkids.org/photographs'
    * The child's missing from location
    * The child's missing since date
    * The child's gender
    * The child's name  

    The webaddress and the html are in order

    Please return your response as JSON
"""

topic_main_page_scraper_system = """You will be shown html that contains links and descriptions of many postings on an adult website. 
Will you extract a LIST of the links to all the postings?
PLEASE RETURN YOUR OUTPUT AS A VALID LIST
"""

adult_ad_scraper_system = """You will be shown html from a webpage that should contain a location, one or more pictures, 
A description of services offered, a title, and possible a phone number and an email address. Can you
extract this info an format it in json?"""

main_page_scraper_system = """You will be shown html from a website that allows user to post ads for goods and services in many 
different categories. Some are legitimate like jobs and real estate, be sure to also include adult services. Parse the html and and return valid 
valid json. key cities should have a value that is a list of all the links without 'terms' or 'post' in the url. 
key services should have a value that is a list of the links to all the content areas with ads. If the link contains 'terms' replace 
it with 'post'
"""


def trafficking_ad_system(keywords: list[str] = trafficking_keywords) -> str:
    prompt = f'''You will be shown a post/advertisement for adult services on a website that may be written by sex_traffickers.
    Look out for any general themes related to extortion or forced sex work. In addition please look for the following key words 
    {keywords}.
    If you believe this ad/post involves human trafficking or sex trafficking please ONLY respond with True, and otherwise please 
    ONLY respond with False.
    '''
    return prompt


def top_most_page_scraper_system(state: str):
    prompt = f"""You will be shown html from a page that offers goods and services. I want you to return a list of all the links to
    pages in the state of {state}. extract the city name from the link it will be of the form: https://<city>.2backpage.com. Return 
    JSON with <city> as the key and the url as the value
"""
    return prompt


## User Prompts


def ncmec_formatter_prompt(html, link):
    prompt = "\n\n".join(
        [
            f"```html: {html}``` \n\n ```webaddress:{link}```"
            for html, link in zip(html, link)
        ]
    )
    return prompt


def ad_scraper_user(batches: list[list[str]]):
    user_prompts = []
    for batch in batches:
        user_prompt = ""
        for page in batch:
            user_prompt += "```HTML START```"
            user_prompt += page
            user_prompt += "```HTML END```"
        user_prompts.append(user_prompt)
    return user_prompts
