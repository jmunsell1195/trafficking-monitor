# Child Protection and Trafficking Detection Project

This project utilizes AI-assisted web scraping, facial recognition, and natural language processing (NLP) to detect sex trafficking and protect children. It scrapes images of missing and exploited children from the National Center for Missing & Exploited Children (NCMEC) website, gathers data from an adult service website known for sex trafficking, and compares the images from both sources using facial recognition. Additionally, it analyzes ads using large language models (LLMs) to detect language indicative of sex trafficking.

## Features
- **Scraping from NCMEC**: Gathers images and information of missing and exploited children.
- **Adult Website Scraping**: Collects ads and associated information, including images and contact details, from known adult service websites.
- **Facial Recognition**: Compares images of missing children from NCMEC to those found in adult website ads using DeepFace.
- **Language Analysis**: Utilizes large language models to detect signs of exploitation or trafficking-related language in ads.

## Prerequisites
Ensure you have the following installed before running the project:
- Python 3.10+
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- [Selenium](https://www.selenium.dev/)
- [DeepFace](https://github.com/serengil/deepface)
- [OpenAI GPT-4](https://openai.com/)
- [MongoDB (PyMongo)](https://pymongo.readthedocs.io/en/stable/)
- [MongoDBServer](https://www.mongodb.com/try/download/community)


## steps
```bash
git clone https://github.com/jmunsell1195/trafficking-monitor
cd trafficking-monitor
pip install -r requirements.txt
```

## Usage
1. Start the api
```bash
python api/api.py
```
2. Use CURL to call available endpoints for
  * ncmec scraper<br/>
    Scrapes missing children data from NCMEC and stores it in the mongo database.
  ```bash
  curl http://localhost:5000/scrape-ncmec
  ```
  * age check <br/>
  Verifies the estimated age of individuals in images (useful for identifying minors in adult ads).
  ```bash
  curl http://localhost:5000/age?img<url-to-image>
  ```
  * backpage scraper<br/>
 Scrapes escort ads from a backpage clone website and stores the collected information, including contact details, in a MongoDB database
  ```bash
  curl http://localhost:5000/scrape-backpage
  ```
  * compare ncmec images to backpage images<br/>
    Compares images from NCMEC and Backpage to identify potential matches. If a match is found, it returns the URLs, the victim's name, and contact information from the ad.
  ```bash
  curl http://localhost:5000/compare-ncmec-bp
  ```
  * search ads for trafficking language and terminology
  This searches through backpage ads and looks for keywords (which can be programmatically updated) and general signs of exploitation
  ```curl 
  http://localhost:5000/search-ads-trafficking
  ```
TODO
- add react frontend
- performance testing


