import requests

url = 'https://www.zameen.com/Property/d_12_d-12_1_4_44_marla_single_unit_luxury_corner_house_with_open_view_cda_sector_d-12_1-53019840-3154-1.html'
output_filename = 'zameen_property.html'

try:
    response = requests.get(url)
    
    if response.status_code == 200:
        html_content = response.text
        
        # Save the content to a file
        with open(output_filename, 'w', encoding='utf-8') as file:
            file.write(html_content)
            
        print(f"Successfully saved HTML to {output_filename}")
            
    else:
        print(f"Error: Failed to retrieve the page. Status code: {response.status_code}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")