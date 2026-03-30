import requests
from bs4 import BeautifulSoup

import sys


def get_cover(url, data):
    if not url or url == "None":
        print(f"[WARN] URL is invalid: {url}, data: {data}")
        return None

    report = open("erros.csv", mode='a')

    try:
        # Send a request to the website
        response = requests.get(url)
        response.raise_for_status()  # optional, ensures we handle bad responses

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the 'div' with the class 'page_content media_image'
        media_image_div = soup.find('div', class_='page_content media_image')

        h1 = soup.find('h1')
        if h1 is not None and "Not" in h1.text:
            report.write(f"\n{data.text}")

        images = media_image_div.find_all('img') if media_image_div else []
        for anchor in images:
            src = anchor.get('src')
            if src:
                return src

    except requests.RequestException as e:
        print(f"[ERROR] Request failed for URL: {url} — {e}")
        report.write(f"\nRequest error for {url} — {data.text}")

    finally:
        report.close()

    return None




def get_bnd_link(url):
    
    
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the 'div' with the class 'page_content media_image'
    bnd_link = soup.find('div', class_='itemDiv')

    # Find the first 'a' (anchor) tag inside the 'itemDiv' div
    if bnd_link:
        first_anchor = bnd_link.find('a')
        if first_anchor:
            anchor_url = first_anchor.get('href')  # Get the href attribute of the anchor
            return anchor_url
        else:
            ""
    else:
        ""

