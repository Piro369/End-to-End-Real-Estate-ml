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
OUTPUT_CSV = "datasets\\final_data_(3301_to_3800_rows).csv"
UPPER_LIMIT = 3800
LOWER_LIMIT = 3301
BUTTON_CLASS_NAME = "_2b94111a"  # The class for the "Send email" button
DETAILS_CLASS_NAME = "_3dc8d08d" # The class for the main property details container
# ---------------------

#
# --- Parsing Functions ---
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
    details_container = soup.find('ul', class_=DETAILS_CLASS_NAME)
    
    if not details_container:
        return data

    details_list = details_container.find_all('li') 
    
    for item in details_list:
        key_span = item.find('span', class_='ed0db22a')
        value_span = item.find('span', class_='_2fdf7fc5')
        
        if key_span and value_span:
            key = clean_text(key_span.get_text())
            value = clean_text(value_span.get_text())
            
            if key == 'Price':
                price_div = value_span.find('div', class_='_2923a568')
                if price_div:
                    value = clean_text(price_div.get_text())
                
            data[key] = value
            
    return data

def extract_description(soup):
    """
    Extracts the property description text.
    """
    description_span = soup.find('span', class_='_3547dac9')
    if description_span:
        description = description_span.get_text(separator='\n', strip=True)
        return clean_text(description)
    return None

def extract_amenities(soup):
    """
    Extracts all amenities, grouped by their category.
    """
    data = {}
    amenities_container = soup.find('ul', class_='_49fc0232')
    
    if not amenities_container:
        return data
        
    categories = amenities_container.find_all('li', class_='_51519f00', recursive=False)
    
    for category in categories:
        title_div = category.find('div', class_='d0142259')
        if not title_div:
            continue
            
        category_title = clean_text(title_div.get_text())
        amenities_list = []
        amenity_items = category.find_all('li', class_='_59261156')
        
        for item in amenity_items:
            amenity_text = clean_text(item.get_text())
            if amenity_text:
                amenities_list.append(amenity_text)
        
        if amenities_list:
            data[f"Amenities: {category_title}"] = ", ".join(amenities_list)
            
    return data

#
# --- Selenium + BS4 Scraper Logic ---
#

def process_url(url, driver):
    """
    Opens a single URL, checks if it's valid, clicks buttons, gets HTML, and parses it.
    """
    try:
        driver.get(url)
        
        # --- NEW FAST CHECK ---
        # Wait max 2 seconds for the core details container to load. 
        # If it doesn't load quickly, the page is likely a dead link or lacks data.
        try:
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CLASS_NAME, DETAILS_CLASS_NAME))
            )
        except Exception:
            # Skip this URL silently to save time
            return None
        # ----------------------

        # If the check passes, we look for the buttons. 
        # Wait time reduced to 4 seconds since the page is already mostly loaded.
        try:
            wait = WebDriverWait(driver, 4) 
            all_buttons = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, BUTTON_CLASS_NAME))
            )
            
            for button in all_buttons:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(0.5) 
                    driver.execute_script("arguments[0].click();", button)
                except Exception as e:
                    print(f"  - Warning: Could not click a button on {url}. Error: {e}")
            
            time.sleep(1) 
        except Exception:
            # If buttons aren't found, we just ignore the error and keep scraping 
            # the data we already confirmed exists.
            pass

        # Parse with BeautifulSoup
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        
        property_data = {'Scraped_URL': url}
        
        # Extract all details
        details = extract_details(soup)
        property_data.update(details)
        
        description = extract_description(soup)
        if description:
            property_data['Description'] = description
            
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
    print("Setting up Selenium WebDriver...")
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--log-level=3') 
    driver = webdriver.Chrome(service=service, options=options)
    
    print(f"Reading data from {INPUT_CSV}...")
    try:
        input_data = pd.read_csv(INPUT_CSV)
        
        # Check if required columns exist
        if URL_COLUMN not in input_data.columns:
            print(f"Error: CSV file '{INPUT_CSV}' must have a column named '{URL_COLUMN}'")
            driver.quit()
            return
            
        if 'Location' not in input_data.columns:
            print(f"Error: CSV file '{INPUT_CSV}' must have a column named 'Location'")
            driver.quit()
            return
        
        # Slice the dataset based on limits
        data_to_scrape = input_data.loc[LOWER_LIMIT:UPPER_LIMIT]
        print(f"Found {len(data_to_scrape)} records to scrape (limit is {LOWER_LIMIT} till {UPPER_LIMIT}).")
        
    except FileNotFoundError:
        print(f"Error: Input file not found: {INPUT_CSV}")
        driver.quit()
        return
    except Exception as e:
        print(f"Error reading CSV: {e}")
        driver.quit()
        return

    all_property_data = []
    print("Starting scraper...")
    
    # Iterate through rows to keep the original Location data linked to the URL
    for index, row in tqdm(data_to_scrape.iterrows(), total=len(data_to_scrape), desc="Scraping pages"):
        url = row[URL_COLUMN]
        original_location = row['Location']
        
        data = process_url(url, driver)
        
        # If scraping succeeded, add the location and append to our main list
        if data:
            data['Real Location'] = original_location
            all_property_data.append(data)
    
    driver.quit()
    print("\nWebDriver closed.")

    if not all_property_data:
        print("No data was scraped. Exiting.")
        return

    print("Creating final dataset...")
    output_data = pd.DataFrame(all_property_data)
    
    # Optional: Reorder columns so 'Real Location' appears right after 'Scraped_URL'
    cols = output_data.columns.tolist()
    if 'Real Location' in cols and 'Scraped_URL' in cols:
        cols.insert(cols.index('Scraped_URL') + 1, cols.pop(cols.index('Real Location')))
        output_data = output_data[cols]
    
    output_data.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f"Successfully scraped {len(output_data)} properties.")
    print(f"Data saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()