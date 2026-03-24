from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os

ser = Service('E:\\Programs\\chromedriver-win64\\chromedriver.exe')
driver = webdriver.Chrome(service= ser)

zameen = pd.read_csv("Zameen_400_Pages.csv")
url_links = zameen['URL'].tolist()

# This is the live URL from the HTML file you provided
TARGET_URL = "https://www.zameen.com/Property/d_12_d-12_2_10_marla_luxury_brand_new_park_face_house_available_for_sale-52432761-3155-1.html"

# This is the class name for the "Send email" button, which appears twice.
DUPLICATE_CLASS_NAME = "_2b5fcdea"

# This will be the name of the file saved *after* clicks
OUTPUT_FILE_NAME = "page_after_clicks.html"

# --- End Configuration ---

# Initialize the WebDriver
# driver = webdriver.Chrome()
driver.maximize_window() # Maximize window for better element visibility

print(f"Attempting to open URL: {TARGET_URL}")

try:
    # Open the live URL
    driver.get(TARGET_URL)

    # Wait for the elements to be present (max 10 seconds)
    # We use find_elements (plural) to get a LIST of all matching elements
    wait = WebDriverWait(driver, 10)
    all_buttons = wait.until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, DUPLICATE_CLASS_NAME))
    )

    print(f"Found {len(all_buttons)} buttons with class name '{DUPLICATE_CLASS_NAME}'.")

    if len(all_buttons) > 1:
        # --- Option 1: Click the FIRST button (index 0) ---
        # This is likely the one in the gallery/image contact form
        print("\n--- Option 1: Clicking the FIRST button ---")
        try:
            first_button = all_buttons[0]
            
            # Scroll to the button to make sure it's viewable
            driver.execute_script("arguments[0].scrollIntoView(true);", first_button)
            print("Scrolled to first button.")
            time.sleep(1) # Pause to observe
            
            # Use JavaScript click as a robust way to click, in case it's obscured
            driver.execute_script("arguments[0].click();", first_button)
            print("Clicked the first button (index 0).")
            
            # Pause to see the effect (if any)
            time.sleep(3)
        except Exception as e:
            print(f"Could not click first button: {e}")


        # --- Option 2: Click the SECOND button (index 1) ---
        # This is likely the one in the sticky contact form on the right
        print("\n--- Option 2: Clicking the SECOND button ---")
        try:
            # We need to find the elements again as the page might have changed
            all_buttons = driver.find_elements(By.CLASS_NAME, DUPLICATE_CLASS_NAME)
            second_button = all_buttons[1]
            
            # Scroll to the button
            driver.execute_script("arguments[0].scrollIntoView(true);", second_button)
            print("Scrolled to second button.")
            time.sleep(1) # Pause to observe
            
            # Click the second button
            driver.execute_script("arguments[0].click();", second_button)
            print("Clicked the second button (index 1).")
            
            time.sleep(3)
        except Exception as e:
            print(f"Could not click second button: {e}")

    elif len(all_buttons) == 1:
        print("Only found 1 button. Clicking it.")
        all_buttons[0].click()
    else:
        print("Error: No buttons found with that class name.")
        
    # --- A More Robust Way (using XPath) ---
    # When classes are duplicated, it's safer to use a more specific
    # path (XPath) to tell Selenium *exactly* which one you want.
    
    print("\n--- Robust Method: Using XPath ---")
    try:
        # This XPath finds the button inside the sticky form on the right
        # by looking for its unique parent (div with class 'f86e30f2')
        sticky_form_button_xpath = "//div[contains(@class, 'f86e30f2')]//button[contains(@class, '_2b94111a')]"
        
        sticky_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, sticky_form_button_xpath))
        )
        
        driver.execute_script("arguments[0].scrollIntoView(true);", sticky_button)
        print("Scrolled to sticky form button using XPath.")
        time.sleep(1)
        
        driver.execute_script("arguments[0].click();", sticky_button)
        print("Clicked the sticky form button using robust XPath.")
    except Exception as e:
        print(f"Could not click button via XPath: {e}")
    
    # --- Save the HTML after interactions ---
    print(f"\nSaving the current page HTML to {OUTPUT_FILE_NAME}...")
    html_content = driver.page_source
    
    with open(OUTPUT_FILE_NAME, 'w', encoding='utf-8') as file:
        file.write(html_content)
        
    print(f"Successfully saved HTML to {os.path.abspath(OUTPUT_FILE_NAME)}")

finally:
    print("\nTest finished. Closing the browser in 5 seconds.")
    time.sleep(5)
    driver.quit()
