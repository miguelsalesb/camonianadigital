import requests
from bs4 import BeautifulSoup

def get_bnd_link(url):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        bnd_link = soup.find('div', class_='itemDiv')

        if bnd_link:
            first_anchor = bnd_link.find('a')
            if first_anchor:
                anchor_url = first_anchor.get('href')
                
                # Skip PDFs before returning the link
                if anchor_url and anchor_url.lower().endswith('.pdf'):
                    print(f"[INFO] Skipping PDF link: {anchor_url}")
                    return None
                    
                return anchor_url
        return None
    
    except requests.RequestException as e:
        print(f"[ERROR] get_bnd_link failed for {url} — {e}")
        return None


def get_cover(url, data):
    if not url or url == "None":
        print(f"[WARN] URL is invalid: {url}, data: {data}")
        return None

    report = open("erros.csv", mode='a')

    try:
        # Check Content-Type before parsing to avoid reading PDFs as HTML
        head_response = requests.head(url, timeout=30)
        content_type = head_response.headers.get('Content-Type', '')
        
        if 'pdf' in content_type.lower():
            print(f"[INFO] Skipping PDF content at: {url}")
            return None

        response = requests.get(url, timeout=30)

        headers = response.headers['Content-Type']
        if 'pdf' in headers:
            print(f"[INFO] Skipping PDF content at: {url}")
            return 'PDF'    


        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

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