import requests
import json
import csv
from datetime import datetime

# Define the API key and domain
api_key = '[redacted]'
domain = 'hts-fs-sandbox'
headers = {'Content-Type': 'application/json'}

# Define the URL for fetching categories
categories_url = f'https://{domain}.freshservice.com/api/v2/solutions/categories'

# Make the API request to fetch categories
response = requests.get(categories_url, headers=headers, auth=(api_key, 'X'))
categories = json.loads(response.text)

# List to store category, folder, and article information
rowArticle = []

# Iterate over the list of categories
for category in categories['categories']:
    category_id = category['id']
    category_name = category['name']
    
    # Define the URL for fetching folders within the category
    folders_url = f'https://{domain}.freshservice.com/api/v2/solutions/folders?category_id={category_id}'
    
    # Make the API request to fetch folders
    folders_response = requests.get(folders_url, headers=headers, auth=(api_key, 'X'))
    folders = json.loads(folders_response.text)
    
    # Iterate over the list of folders
    for folder in folders['folders']:
        folder_id = folder['id']
        folder_name = folder['name']
        
        # Define the URL for fetching articles within the folder
        articles_url = f'https://{domain}.freshservice.com/api/v2/solutions/articles?folder_id={folder_id}'
        
        # Make the API request to fetch articles
        articles_response = requests.get(articles_url, headers=headers, auth=(api_key, 'X'))
        articles = json.loads(articles_response.text)
        
        # Iterate over the list of articles and append to rowArticle
        for article in articles['articles']:
            rowArticle.append({
                'Category ID': category_id,
                'Category Name': category_name,
                'Folder ID': folder_id,
                'Folder Name': folder_name,
                'Article ID': article['id'],
                'Title': article['title'],
                'Description Text': article.get('description_text', ''),
                'Created At': article['created_at'],
                'Updated At': article['updated_at'],
                'Status': article['status'],
                'Approval Status': article.get('approval_status', ''),
                'Thumbs Up': article.get('thumbs_up', 0),
                'Thumbs Down': article.get('thumbs_down', 0),
                'Modified By': article.get('modified_by', ''),
                'Modified At': article.get('modified_at', ''),
                'Inserted Into Tickets': article.get('inserted_into_tickets', 0),
                'Article Type': article.get('article_type', ''),
                'Agent ID': article.get('agent_id', ''),
                'Views': article.get('views', 0),
                'Keywords': article.get('keywords', ''),
                'Review Date': article.get('review_date', ''),
                'URL': article.get('url', ''),
                'Attachments': article.get('attachments', ''),
                #'Description': article.get('description', '')
            })

# Get the current timestamp and format it
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Define the CSV file name with timestamp
csv_file = f'Freshservice_KB_Export_{domain}_{timestamp}.csv'

# Define the CSV headers
csv_headers = [
    'Category ID', 'Category Name', 
    'Folder ID', 'Folder Name',
    'Article ID', 'Title', 
    'Description Text', 
    'Created At', 
    'Updated At', 'Status', 
    'Approval Status', 'Thumbs Up', 
    'Thumbs Down', 'Modified By', 
    'Modified At', 'Inserted Into Tickets',
    'Article Type', 
    'Agent ID',
    'Views', 'Keywords',
    'Review Date', 
    'URL',
    'Attachments',
    #'Description'
]

# Write the categories, folders, and articles to the CSV file
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()
    for row in rowArticle:
        writer.writerow(row)

print(f"All categories, folders, and articles have been exported to {csv_file}.")
