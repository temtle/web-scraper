import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Cache-Control": "max-age=0",
}

visited_urls = set()
sum = 0
counter = 0
average = 0

# Define the function to get info of a product from its url
def get_product_info(url):
    response = requests.get(url, headers=headers)# , proxies=proxies

    # Check response status
    if response.status_code != 200:
        print(f"Response status is {response.status_code}", flush=True)

    # Use BeautifulSoup to parse and scrape site
    soup = BeautifulSoup(response.text, "lxml")

    # Product Title
    title_element = soup.select_one("#productTitle")
    title = title_element.text.strip() if title_element else None

    # Product Rating out of 5 stars
    rating_element = soup.select_one("#acrPopover")
    rating_text = rating_element.attrs.get("title") if rating_element else None
    rating = rating_text.replace("out of 5 stars", "") if rating_text else None

    # Product price
    price_element = soup.select_one("span.a-offscreen")
    price = price_element.text if price_element else None
    try:
        price = float(price)
    except:
        price = "No price listed"

    # Product Image
    image_element = soup.select_one("#landingImage")
    image = image_element.attrs.get("src") if image_element else None

    # Product Description
    '''description_element = soup.select_one("#productDescription").text.strip()
    description = description_element.text.strip() if description_element else None'''

    sum += price
    counter += 1
    
    return {
        "title": title,
        "price": price,
        "rating": rating,
        "image": image,
        '''"description": description,'''
        "url": url
    }

# Define the function to parse through the products in a listing and scrape each product
def parse_listing(listing_url):
    global visited_urls
    response = requests.get(listing_url, headers=headers)
    if response.status_code != 200:
        print(f"Status code is {response.status_code}", flush=True)
    soup_search = BeautifulSoup(response.text, "lxml")
    link_elements = soup_search.select("[data-cy='title-recipe'] > a.a-link-normal")
    page_data = []

    for link_element in link_elements:
        full_url = urljoin(listing_url, link_element.attrs.get("href"))
        if full_url not in visited_urls:
            visited_urls.add(full_url)
            product_info = get_product_info(full_url)
            if product_info:
                page_data.append(product_info)
    
    # Pagination section here, remove triple quotes to go brrrrr
    '''next_page_element = soup_search.select_one("a.s-pagination-next")
    if next_page_element:
        next_page_url = next_page_element.attrs.get("href")
        next_page_url = urljoin(listing_url, next_page_url)
        print(f"Moving onto next page: {next_page_url}", flush=True)
        Recursively check the next page
        page_data += parse_listing(next_page_url)'''

    return page_data

# Use pandas in main to put page_data in a csv file
def main():
    data = []
    search_url = "" # PUT SEARCH URL HERE!!!
    data = parse_listing(search_url)
    pd.DataFrame(data).to_csv("laptops.csv", index=False)
    average = sum / counter

if __name__ == "__main__":
    main()