import pandas as pd
from bs4 import BeautifulSoup
import re

# --- Configuration ---
HTML_FILE_PATH = 'zameen_property.html'
# ---------------------

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
        print("Warning: Could not find details container with class '_3dc8d08d'")
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

def main():
    """
    Main function to read HTML, parse data, and create a DataFrame.
    """
    try:
        with open(HTML_FILE_PATH, 'r', encoding='utf-8') as file:
            html_content = file.read()
    except FileNotFoundError:
        print(f"Error: The file '{HTML_FILE_PATH}' was not found.")
        print("Please make sure it's in the same directory as this script.")
        return
    except Exception as e:
        print(f"An error occurred reading the file: {e}")
        return

    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # This dictionary will hold all our data
    property_data = {}
    
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
    
    # Create a DataFrame from the dictionary
    # We wrap the dictionary in a list to create a single-row DataFrame
    df = pd.DataFrame([property_data])
    
    # Print the DataFrame
    print("Successfully extracted data into DataFrame:")
    print(df)
    
    # Optionally, save to a CSV file
    output_csv = 'property_details.csv'
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\nDataFrame also saved to '{output_csv}'")

if __name__ == "__main__":
    main()