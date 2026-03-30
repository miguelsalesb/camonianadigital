import requests
import re
import csv
from bs4 import BeautifulSoup


def get_bnd_link(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    bnd_link = soup.find('div', class_='itemDiv')

    if bnd_link:
        first_anchor = bnd_link.find('a')
        if first_anchor:
            anchor_url = first_anchor.get('href')
            return anchor_url
    return ""


def follow_redirect(url):
    response = requests.get(url, allow_redirects=True)
    return response.url


def extract_number_from_url(url):
    numbers = re.findall(r'\d+', url)
    return numbers[-1] if numbers else ""


def get_cover(subfield):
    bnd_link = get_bnd_link(subfield)

    if bnd_link:
        final_url = follow_redirect(bnd_link)
        number = extract_number_from_url(final_url)
        return number

    return ""


# Read URLs from CSV and save results to a new CSV
input_file = 'links-purls.csv'
output_file = 'links-bndigital.csv'

with open(input_file, newline='', encoding='utf-8') as infile, \
     open(output_file, 'w', newline='', encoding='utf-8') as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Write header to output CSV
    writer.writerow(['url', 'number'])

    for row in reader:
        if row:  # Skip empty rows
            url = row[0].strip()
            print(f"Processing: {url}")
            result = get_cover(url)
            writer.writerow([url, result])
            print(f"  → Result: {result}")

print(f"\nDone! Results saved to '{output_file}'")