import pandas as pd
from bs4 import BeautifulSoup
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm  # Used to show a nice progress bar

# --- Configuration ---
INPUT_CSV = "Zameen_400_Pages.csv"
URL_COLUMN = "URL"
OUTPUT_CSV = "final_data_(2601_to_3000_rows).csv"
URL_LIMIT = 10  # Scrape the first 10 URLs as requested
UPPER_LIMIT = 3000
LOWER_LIMIT = 2601
BUTTON_CLASS_NAME = "_2b94111a"  # The class for the "Send email" button
# ---------------------
#
# --- Parsing Functions (from extract_property_details.py) ---
#

def clean_text(text):
    """Utility function to clean up extracted text."""
    if text:
        # Remove multiple spaces and newlines
        return re.sub(r'\s+', ' ', text).strip()
    return None

def extract_details(soup):
    """
    Extracts key-value pairs from the 'Details' section.
    These are in an <ul> with class '_3dc8d08d'.
    """
    data = {}
    # First, find the container list
    details_container = soup.find('ul', class_='_3dc8d08d')
    
    if not details_container:
        # Don't print a warning for every page, just return empty
        return data

    # Now, find all 'li' items inside that container
    details_list = details_container.find_all('li') 
    
    for item in details_list:
        # The first span is the key (e.g., "Type")
        key_span = item.find('span', class_='ed0db22a')
        # The second span is the value (e.g., "House")
        value_span = item.find('span', class_='_2fdf7fc5')
        
        if key_span and value_span:
            key = clean_text(key_span.get_text())
            value = clean_text(value_span.get_text())
            
            # Special handling for Price, as it's nested
            if key == 'Price':
                price_div = value_span.find('div', class_='_2923a568')
                if price_div:
                    value = clean_text(price_div.get_text())
                
            data[key] = value
            
    return data

def extract_description(soup):
    """
    Extracts the property description text.
    This is inside a span with class '_3547dac9'.
    """
    description_span = soup.find('span', class_='_3547dac9')
    if description_span:
        # Use .get_text() with a separator to handle <br> tags gracefully
        description = description_span.get_text(separator='\n', strip=True)
        return clean_text(description)
    return None

def extract_amenities(soup):
    """
    Extracts all amenities, grouped by their category.
    The main container is '_49fc0232'.
    """
    data = {}
    amenities_container = soup.find('ul', class_='_49fc0232')
    
    if not amenities_container:
        return data
        
    # Each 'li' inside is a category (e.g., "Main Features", "Rooms")
    categories = amenities_container.find_all('li', class_='_51519f00', recursive=False)
    
    for category in categories:
        # Find the category title
        title_div = category.find('div', class_='d0142259')
        if not title_div:
            continue
            
        category_title = clean_text(title_div.get_text())
        
        # Find all amenities listed within this category
        amenities_list = []
        amenity_items = category.find_all('li', class_='_59261156')
        
        for item in amenity_items:
            amenity_text = clean_text(item.get_text())
            if amenity_text:
                amenities_list.append(amenity_text)
        
        # Join the list of amenities with a comma for a single DataFrame cell
        if amenities_list:
            data[f"Amenities: {category_title}"] = ", ".join(amenities_list)
            
    return data

#
# --- Selenium + BS4 Scraper Logic ---
#

def process_url(url, driver):
    """
    Opens a single URL, clicks buttons, gets HTML, and parses it.
    Returns a dictionary of scraped data.
    """
    try:
        driver.get(url)
        # Wait a max of 10 seconds for the buttons to appear
        wait = WebDriverWait(driver, 10) 

        # Wait for at least one button to be present
        all_buttons = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, BUTTON_CLASS_NAME))
        )
        
        # Click all buttons found (usually 2)
        for button in all_buttons:
            try:
                # Use JavaScript click as it's more reliable
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(0.5) # Short pause for scroll
                driver.execute_script("arguments[0].click();", button)
            except Exception as e:
                # Log a warning but continue the script
                print(f"  - Warning: Could not click a button on {url}. Error: {e}")
        
        # Wait 1 second for any JS to execute after clicking
        # Note: This is part of the delay you mentioned for scaling.
        time.sleep(1) 

        # Now that clicks are done, get the page source
        html_content = driver.page_source
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # This dictionary will hold all our data for this one property
        property_data = {}
        
        # Add the URL itself so we know which property this is
        property_data['Scraped_URL'] = url
        
        # 1. Extract Details
        details = extract_details(soup)
        property_data.update(details)
        
        # 2. Extract Description
        description = extract_description(soup)
        if description:
            property_data['Description'] = description
            
        # 3. Extract Amenities
        amenities = extract_amenities(soup)
        property_data.update(amenities)
        
        return property_data

    except Exception as e:
        print(f"  - ERROR: Failed to process {url}. Error: {e}")
        return None

#
# --- Main Orchestrator ---
#

def main():
    # 1. Setup Selenium Driver
    print("Setting up Selenium WebDriver...")
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # Run in headless mode (no browser window) for speed and scaling
    options.add_argument('--headless')
    options.add_argument('--log-level=3') # Suppress non-fatal console logs
    driver = webdriver.Chrome(service=service, options=options)
    
    # 2. Read Input CSV
    print(f"Reading URLs from {INPUT_CSV}...")
    try:
        df_input = pd.read_csv(INPUT_CSV)
        if URL_COLUMN not in df_input.columns:
            print(f"Error: CSV file '{INPUT_CSV}' must have a column named '{URL_COLUMN}'")
            driver.quit()
            return
        
        urls_to_scrape = df_input[URL_COLUMN].loc[LOWER_LIMIT:UPPER_LIMIT].tolist()
        print(f"Found {len(urls_to_scrape)} URLs to scrape (limit is {LOWER_LIMIT} till {UPPER_LIMIT}).")
        
    except FileNotFoundError:
        print(f"Error: Input file not found: {INPUT_CSV}")
        driver.quit()
        return
    except Exception as e:
        print(f"Error reading CSV: {e}")
        driver.quit()
        return

    # 3. Loop and Scrape
    all_property_data = []
    print("Starting scraper...")
    
    # Use tqdm for a progress bar
    for url in tqdm(urls_to_scrape, desc="Scraping pages"):
        data = process_url(url, driver)
        if data:
            all_property_data.append(data)
    
    # 4. Quit Driver
    driver.quit()
    print("\nWebDriver closed.")

    # 5. Create Final DataFrame
    if not all_property_data:
        print("No data was scraped. Exiting.")
        return

    print("Creating final DataFrame...")
    df_output = pd.DataFrame(all_property_data)
    
    # 6. Save Output CSV
    df_output.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f"Successfully scraped {len(df_output)} properties.")
    print(f"Data saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()