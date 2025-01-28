import requests
import json
import csv
from datetime import datetime

# Define the API key and domain
api_key = '[redacted]'
domain = 'hts-fs-sandbox'
headers = {'Content-Type': 'application/json'}

# Function to fetch service items with pagination
def fetch_service_items(page):
    service_items_url = f'https://{domain}.freshservice.com/api/v2/service_catalog/items?per_page=100&page={page}&workspace_id=0'
    response = requests.get(service_items_url, headers=headers, auth=(api_key, 'X'))
    return json.loads(response.text)

# List to store service item information
rowServiceItems = []
page = 1

while True:
    service_items = fetch_service_items(page)
    items = service_items['service_items']
    
    if not items:
        break
    
    for item in items:
        rowServiceItems.append({
            'ID': item['id'],
            'Workspace ID': item.get('workspace_id', ''),
            'Created At': item['created_at'],
            'Updated At': item['updated_at'],
            'Name': item['name'],
            'Delivery Time': item.get('delivery_time', 0),
            'Display ID': item.get('display_id', ''),
            'Category ID': item.get('category_id', ''),
            'Product ID': item.get('product_id', ''),
            'Quantity': item.get('quantity', 0),
            'Deleted': item.get('deleted', False),
            'Group Visibility': item.get('group_visibility', 0),
            'Item Type': item.get('item_type', 0),
            'CI Type ID': item.get('ci_type_id', ''),
            'Cost Visibility': item.get('cost_visibility', False),
            'Delivery Time Visibility': item.get('delivery_time_visibility', False),
            'Configs': item.get('configs', ''),
            'Botified': item.get('botified', False),
            'Visibility': item.get('visibility', 0),
            'Allow Attachments': item.get('allow_attachments', False),
            'Allow Quantity': item.get('allow_quantity', False),
            'Is Bundle': item.get('is_bundle', False),
            'Create Child': item.get('create_child', False),
            'Description': item.get('description', ''),
            'Short Description': item.get('short_description', ''),
            'Cost': item.get('cost', 0),
            'Custom Fields': item.get('custom_fields', ''),
            'Child Items': item.get('child_items', '')
        })
    
    if len(items) < 100:
        break
    
    page += 1

# Get the current timestamp and format it
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Define the CSV file name with timestamp
csv_file = f'Freshservice_Service_Items_Export_{domain}_{timestamp}.csv'

# Define the CSV headers
csv_headers = [
    'ID', 'Workspace ID', 'Created At', 'Updated At', 'Name', 
    'Delivery Time', 'Display ID', 'Category ID', 'Product ID', 
    'Quantity', 'Deleted', 'Group Visibility', 'Item Type', 
    'CI Type ID', 'Cost Visibility', 'Delivery Time Visibility', 
    'Configs', 'Botified', 'Visibility', 'Allow Attachments', 
    'Allow Quantity', 'Is Bundle', 'Create Child', 'Description', 
    'Short Description', 'Cost', 'Custom Fields', 'Child Items'
]

# Write the service items to the CSV file
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()
    for row in rowServiceItems:
        writer.writerow(row)

print(f"All service items have been exported to {csv_file}.")