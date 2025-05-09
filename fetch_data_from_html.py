import requests
from bs4 import BeautifulSoup
import csv

# Read URLs from a file and strip newline characters
with open("data/urls.txt", 'r') as file:
    urls = [url.strip() for url in file.readlines()]

# Function to extract information from a given URL
def extract_info(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve {url}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extracting Title
    title = soup.find('h1', class_='jet-listing-dynamic-field__content')
    title = title.get_text(strip=True) if title else 'N/A'

    # Extracting Category
    category_element = soup.find('p', text='Category')
    category = category_element.find_next('div', class_='jet-listing-dynamic-field__content').get_text(strip=True) if category_element else 'N/A'

    # Extracting Institutions
    institutions_element = soup.find('p', text='Institutions')
    institutions = institutions_element.find_next('div', class_='jet-listing-dynamic-field__content').get_text(strip=True) if institutions_element else 'N/A'

    # Extracting Data type
    data_type_element = soup.find('p', text='Data type')
    data_type = data_type_element.find_next('div', class_='jet-listing-dynamic-field__content').get_text(strip=True) if data_type_element else 'N/A'

    # Extracting Field
    field_element = soup.find('p', text='Field')
    field = field_element.find_next('div', class_='jet-listing-dynamic-field__content').get_text(strip=True) if field_element else 'N/A'

    # Extracting Researchers
    researchers_element = soup.find('p', text='Researchers')
    researchers = researchers_element.find_next('div', class_='jet-listing-dynamic-field__content').get_text(strip=True) if researchers_element else 'N/A'

    # Extracting Abstract
    abstract_element = soup.find('p', text='Abstract')
    abstract = abstract_element.find_next('div', class_='jet-listing-dynamic-field__content').get_text(strip=True) if abstract_element else 'N/A'

    return {
        'URL': url,
        'Title': title,
        'Category': category,
        'Institutions': institutions,
        'Data type': data_type,
        'Field': field,
        'Researchers': researchers,
        'Abstract': abstract
    }

# Extract information from all URLs and save to CSV
csv_file = 'data/data.csv'
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['URL', 'Title', 'Category', 'Institutions', 'Data type', 'Field', 'Researchers', 'Abstract'])
    writer.writeheader()

    for url in urls:
        info = extract_info(url)
        if info:
            writer.writerow(info)

print(f"Data has been saved to {csv_file}")
