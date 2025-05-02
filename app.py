# 📁 shelfai_apify_fetcher/app.py
from flask import Flask, request, jsonify, render_template
import requests
import time
import os

app = Flask(__name__)

APIFY_TOKEN = os.getenv('APIFY_TOKEN')  # Save this in your .env file
SCRAPER_ACTOR = 'junglee/free-amazon-product-scraper'

# Step 1: Trigger the Apify scraper

def start_scraper(product_url):
    run_url = f'https://api.apify.com/v2/acts/{SCRAPER_ACTOR}/runs?token={APIFY_TOKEN}'

    payload = {
        "startUrls": [{"url": product_url}],
        "maxItems": 1
    }

    response = requests.post(run_url, json=payload)
    run_id = response.json()['data']['id']
    return run_id

# Step 2: Wait and fetch the results

def get_scraper_results(run_id):
    status_url = f'https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}'

    while True:
        status = requests.get(status_url).json()['data']['status']
        if status == 'SUCCEEDED':
            break
        elif status == 'FAILED':
            raise Exception("Scraper run failed")
        time.sleep(5)

    dataset_url = f'https://api.apify.com/v2/actor-runs/{run_id}/dataset/items?token={APIFY_TOKEN}&format=json'
    data = requests.get(dataset_url).json()
    return data[0]  # First item

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch', methods=['POST'])
def fetch():
    product_url = request.form.get('url')
    try:
        run_id = start_scraper(product_url)
        product_data = get_scraper_results(run_id)
        return render_template('result.html', data=product_data)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
