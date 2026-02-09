import pandas as pd
from bs4 import BeautifulSoup
import requests
import time

def scrape_zameen_pages(total_pages=400):
    """
    Scrapes property listings from Zameen.com for the specified number of pages.
    
    Args:
        total_pages (int): The number of pages to scrape (e.g., 10).

    Returns:
        pd.DataFrame: A DataFrame containing the extracted property data from all pages.
    """
    
    all_properties_list = []
    base_url = "https://www.zameen.com"
    
    # We must send headers to identify ourselves as a browser,
    # otherwise, the website will likely block our request.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print("Starting the scraping process...")

    for page_number in range(300, total_pages + 1):
        # Format the URL for the current page
        url = f"https://www.zameen.com/Homes/Islamabad-3-{page_number}.html"
        print(f"\nFetching page: {url}...")
        
        try:
            # --- Make the HTTP request to the live website ---
            response = requests.get(url, headers=headers)
            
            # Check if the request was successful
            if response.status_code != 200:
                print(f"  Failed to fetch page {page_number}. Status Code: {response.status_code}")
                print("  This might be due to anti-scraping measures (like CAPTCHA) or the page not existing.")
                print("  Skipping this page.")
                continue # Skip to the next page

            # --- Parse the HTML content ---
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all property listing containers
            listings = soup.find_all('li', {'aria-label': 'Listing'})
            
            if not listings:
                print(f"  No listings found on page {page_number}. The website structure might have changed or we were blocked.")
                continue

            print(f"  Found {len(listings)} listings on page {page_number}.")

            # --- Loop through each listing on the page ---
            for listing in listings:
                try:
                    # --- Extract Title ---
                    title_tag = listing.find('h2', {'aria-label': 'Title'})
                    title = title_tag.text.strip() if title_tag else 'N/A'

                    # --- Extract Price ---
                    price_tag = listing.find('span', {'aria-label': 'Price'})
                    currency_tag = listing.find('span', {'aria-label': 'Currency'})
                    price = f"{currency_tag.text.strip()} {price_tag.text.strip()}" if price_tag and currency_tag else 'N/A'

                    # --- Extract Location ---
                    location_tag = listing.find('div', {'aria-label': 'Location'})
                    location = location_tag.text.strip() if location_tag else 'N/A'

                    # --- Extract Beds ---
                    beds_tag = listing.find('span', {'aria-label': 'Beds'})
                    beds = beds_tag.text.strip() if beds_tag else 'N/A'

                    # --- Extract Baths ---
                    baths_tag = listing.find('span', {'aria-label': 'Baths'})
                    baths = baths_tag.text.strip() if baths_tag else 'N/A'

                    # --- Extract Area ---
                    area_tag = listing.find('span', {'aria-label': 'Area'})
                    area = area_tag.text.strip() if area_tag else 'N/A'

                    # --- Extract Property URL ---
                    url_tag = listing.find('a', {'aria-label': 'Listing link'})
                    url = f"{base_url}{url_tag['href']}" if url_tag and url_tag.get('href') else 'N/A'

                    # --- Extract Listing Badge ---
                    badge_tag = listing.find('div', class_=lambda x: x and x.startswith('_021a5aeb'))
                    badge = badge_tag.text.strip() if badge_tag else 'N/A'

                    # --- Extract Date Added/Updated ---
                    date_tag = listing.find('span', {'aria-label': 'Listing creation date'})
                    date_added = date_tag.text.strip() if date_tag else 'N/A'

                    # Append data as a dictionary to our main list
                    prop_data = {
                        "Page": page_number,
                        "Title": title,
                        "Price": price,
                        "Location": location,
                        "Beds": beds,
                        "Baths": baths,
                        "Area": area,
                        "Badge": badge,
                        "Date Added": date_added,
                        "URL": url,
                    }
                    all_properties_list.append(prop_data)
                
                except Exception as e:
                    print(f"    Error parsing one listing: {e}")
                    pass # Continue to the next listing

            # --- Be polite to the server ---
            # Wait for 2 seconds before fetching the next page
            print("  Waiting 2 seconds before next page...")
            time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"  An error occurred during the request for page {page_number}: {e}")
            print("  Skipping this page.")
            continue
            
    print(f"\nScraping complete. Total properties extracted: {len(all_properties_list)}")
    
    # Convert the list of dictionaries into a pandas DataFrame
    df = pd.DataFrame(all_properties_list)
    return df

if __name__ == "__main__":
    # --- Instructions ---
    # 1. Make sure you have pandas, beautifulsoup4, and requests installed:
    #    pip install pandas beautifulsoup4 requests
    #    (or use the requirements.txt file)
    # --------------------

    properties_df = scrape_zameen_pages()
    
    if not properties_df.empty:
        print("\n--- Extracted Data (First 5 Rows) ---")
        print(properties_df.head())
        
        # Save the DataFrame to a CSV file
        try:
            csv_filename = 'zameen_properties_300_to_400_pages.csv'
            properties_df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            print(f"\nSuccessfully extracted {len(properties_df)} properties.")
            print(f"Data saved to '{csv_filename}'")
        except Exception as e:
            print(f"Error saving data to CSV: {e}")
    else:
        print("\nNo data was extracted. The DataFrame is empty.")