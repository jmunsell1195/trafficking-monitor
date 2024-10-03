import asyncio

import requests
from flask import Flask, request
from openai_models import gpt4_main_page_scraper, gpt4_trafficking_keywords
from prompts import top_most_page_scraper_system
from pymongo import MongoClient
from scrapers.backpage_scraper import scrape_by_state
from scrapers.ncmec_scraper import scrape_ncmec
from utils import get_np_image, us_states

from deepface import DeepFace

mongo_client = MongoClient("mongodb://localhost:27017")


app = Flask(__name__)


def get_matches():
    ncmec_db = mongo_client["ncmec_data"]
    records = ncmec_db["records"]
    ncmec_records = records.find({}).limit(10)
    matches = []
    bp_db = mongo_client["backpageTexas"]
    posts = bp_db["sanAntonio"]
    posts = posts.find({}).limit(10)

    for post in posts:
        bp_image_url = post["images"][0]
        bp_image = get_np_image(requests.get(bp_image_url))
        print(bp_image_url)
        for record in ncmec_records:
            ncmec_image_url = record["photo_link"]
            print(ncmec_image_url)
            ncmec_image = get_np_image(requests.get(ncmec_image_url))
            try:
                match = DeepFace.verify(
                    ncmec_image,
                    bp_image,
                    model_name="DeepFace",
                    enforce_detection=False,
                    threshold=0.9,
                )
                print(match)
                if match["verified"]:
                    matches.append(
                        {
                            "name": record["name"],
                            "bp-image": bp_image_url,
                            "ncmec-image": ncmec_image_url,
                            "bp-phone": post["phone"],
                            "bp-email": post["email"],
                        }
                    )
                else:
                    matches.append("no-match")
            except Exception as e:
                print(e)
                pass
    return matches


@app.route("/verify")
def verify():
    img1 = request.args["img1"]
    img2 = request.args["img2"]

    img1 = get_np_image(requests.get(img1))
    img2 = get_np_image(requests.get(img2))

    try:
        result = DeepFace.verify(
            img1_path=img1,
            img2_path=img2,
            model_name="DeepFace",
            threshold=0.45,
            enforce_detection=False,
        )
        return {"ok": True, "result": result["verified"]}
    except Exception as e:
        return {"ok": False, "result": e}


@app.route("/age")
def get_age():
    img = request.args["img"]
    img = get_np_image(requests.get(img))

    try:
        result = DeepFace.analyze(img, actions=["age"], enforce_detection=False)
        return {"ok": True, "age": result[0]["age"]}
    except Exception as e:
        return {"ok": False, "result": None}


@app.route("/get-cities")
def get_cities():
    state = request.args["state"]
    if state.lower() in us_states:
        base_url = "https://www.2backpage.com/"
        front_page_html = requests.get(base_url).text
        cities_list_for_state = gpt4_main_page_scraper(
            page_html=front_page_html, system=top_most_page_scraper_system(state=state)
        )
        cities_list = [city for city in cities_list_for_state.keys()]
        print(cities_list)
        return {"ok": True, "result": cities_list}
    return {"ok": False, "result": f"{state} is not a US State"}


@app.route("/scrape-backpage")
def scrape_backpage(num_pages_to_scrape: int = 10):
    state = request.args["state"]
    city = request.args["city"]
    n_pages = request.args["pages"]
    if n_pages:
        num_pages_to_scrape = n_pages
    if state.lower() not in us_states:
        return {"ok": False, "result": f"{state} is not a US State"}
    try:
        scrape_by_state(state=state, city=city, num_pages_to_scrape=num_pages_to_scrape)
        return {
            "ok": True,
            "result": f"{num_pages_to_scrape} pages successully scraped",
        }
    except Exception as e:
        return {"ok": False, "result": f"There was an exception: {e}"}


@app.route("/scrape-ncmec")
def ncmec_scraper():
    try:
        scrape_ncmec()
        return {"ok": True, "result": "Scrapin finished successfully"}
    except Exception as e:
        return {"ok": False, "result": f"There was an exception: {e}"}


@app.route("/compare-ncmec-bp")
def compare_ncmec_bp():
    try:
        matches = get_matches()
        return {"ok": True, "result": matches}
    except Exception as e:
        return {"ok": False, "result": str(e)}
    
@app.route('/search-ads-trafficking')
def search_ads(client: MongoClient = mongo_client, limit: int = 10):
    matches = []
    ads = client['backpageTexas']
    ads_collection = ads['sanAntonio']
    posts = ads_collection.find().limit(limit)
    for post in posts:
        ## ObjectId is not json serializable
        del post["_id"]
        try:
            text_to_analyze = post['description']
            if gpt4_trafficking_keywords(user=text_to_analyze):
                matches.append(post)
        except Exception as e:
            matches.append(str(e))
    return {'ok':True,'matches':matches}






if __name__ == "__main__":
    app.run(port="5000", debug=True)
