import pandas as pd
from bs4 import BeautifulSoup

def parse_zameen_html(filepath):
    """
    Parses the Zameen.com HTML file to extract property listings.
    
    Args:
        filepath (str): The path to the HTML file.

    Returns:
        pd.DataFrame: A DataFrame containing the extracted property data.
    """
    print(f"Opening and parsing file: {filepath}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        print("Please make sure the HTML file is in the same directory as this script.")
        return pd.DataFrame() # Return an empty DataFrame
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return pd.DataFrame()

    soup = BeautifulSoup(content, 'html.parser')
    
    # Find all property listing containers
    # We use aria-label="Listing" as it's a stable identifier, unlike the scrambled CSS classes.
    listings = soup.find_all('li', {'aria-label': 'Listing'})
    
    print(f"Found {len(listings)} listings on the page.")
    
    properties_list = []
    base_url = "https://www.zameen.com"

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

            # --- Extract Listing Badge (e.g., "Super Hot") ---
            badge_tag = listing.find('div', class_=lambda x: x and x.startswith('_021a5aeb')) # Find class starting with _021a5aeb
            badge = badge_tag.text.strip() if badge_tag else 'N/A'

            # --- Extract Date Added/Updated ---
            date_tag = listing.find('span', {'aria-label': 'Listing creation date'})
            date_added = date_tag.text.strip() if date_tag else 'N/A'

            # Append data as a dictionary to our list
            prop_data = {
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
            properties_list.append(prop_data)
        
        except Exception as e:
            print(f"Error parsing one listing: {e}")
            # Continue to the next listing even if one fails
            pass

    # Convert the list of dictionaries into a pandas DataFrame
    df = pd.DataFrame(properties_list)
    return df

if __name__ == "__main__":
    # --- Instructions ---
    # 1. Make sure you have pandas and beautifulsoup4 installed:
    #    pip install pandas beautifulsoup4
    #
    # 2. Make sure the HTML file 'zameen_isb.html' is in the
    #    same folder as this Python script.
    # --------------------

    filepath = 'zameen_isb.html'
    properties_df = parse_zameen_html(filepath)
    
    if not properties_df.empty:
        print("\n--- Extracted Data (First 5 Rows) ---")
        print(properties_df.head())
        
        # Save the DataFrame to a CSV file
        try:
            csv_filename = 'zameen_properties.csv'
            properties_df.to_csv(csv_filename, index=False, encoding='utf-8')
            print(f"\nSuccessfully extracted {len(properties_df)} properties.")
            print(f"Data saved to '{csv_filename}'")
        except Exception as e:
            print(f"Error saving data to CSV: {e}")