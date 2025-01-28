import requests
import json
import csv
from datetime import datetime

# Define the API key and domain
api_key = '[redacted]'
domain = 'hts-fs-sandbox'
headers = {'Content-Type': 'application/json'}

url = f'https://{domain}.freshservice.com/api/v2/services'

def fetch_services():
    # Make the API request to fetch categories
    response = requests.get(url, headers=headers, auth=(api_key, 'X'))
    
    if response.status_code == 200:
        services = response.json().get('results', [])
        return services
    else:
        print(f"Failed to retrieve services. Status code: {response.status_code}")
        print("Response:", response.text)
        return None

# Call the function to fetch services
services = fetch_services()