import requests
import json
import csv
from datetime import datetime

# Define the API key and domain
api_key = '[redacted]'
domain = 'hts'
headers = {'Content-Type': 'application/json'}

# Function to fetch canned response folders with pagination
def fetch_canned_response_folders(page):
    canned_response_folders_url = f'https://{domain}.freshservice.com/api/v2/canned_response_folders?per_page=100&page={page}'
    response = requests.get(canned_response_folders_url, headers=headers, auth=(api_key, 'X'))
    return json.loads(response.text)

# Function to fetch canned responses for a specific folder
def fetch_canned_responses(folder_id):
    canned_responses_url = f'https://{domain}.freshservice.com/api/v2/canned_response_folders/{folder_id}/canned_responses'
    response = requests.get(canned_responses_url, headers=headers, auth=(api_key, 'X'))
    return json.loads(response.text)

# List to store canned response folder information
rowCannedResponseFolders = []
page = 1

while True:
    canned_response_folders = fetch_canned_response_folders(page)
    folders = canned_response_folders['canned_response_folders']
    
    if not folders:
        break
    
    for folder in folders:
        folder_info = {
            'Folder ID': folder['id'],
            'Folder Name': folder['name'],
            'Folder Description': folder.get('description', ''),
            'Folder Created At': folder['created_at'],
            'Folder Updated At': folder['updated_at'],
            'Canned Responses': []
        }
        
        # Fetch canned responses for the current folder
        canned_responses = fetch_canned_responses(folder['id'])
        responses = canned_responses['canned_responses']
        
        for response in responses:
            folder_info['Canned Responses'].append({
                'Response ID': response['id'],
                'Response Title': response['title'],
                'Response Content': response['content'],
                'Response Created At': response['created_at'],
                'Response Updated At': response['updated_at']
            })
        
        rowCannedResponseFolders.append(folder_info)
    
    if len(folders) < 100:
        break
    
    page += 1

# Get the current timestamp and format it
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Define the CSV file name with timestamp
csv_file = f'Freshservice_Canned_Response_Folders_Export_{domain}_{timestamp}.csv'

# Define the CSV headers
csv_headers = [
    'Folder ID', 'Folder Name', 'Folder Description', 'Folder Created At', 'Folder Updated At',
    'Response ID', 'Response Title', 'Response Content', 'Response Created At', 'Response Updated At'
]

# Write the canned response folders and responses to the CSV file
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()
    for folder in rowCannedResponseFolders:
        for response in folder['Canned Responses']:
            writer.writerow({
                'Folder ID': folder['Folder ID'],
                'Folder Name': folder['Folder Name'],
                'Folder Description': folder['Folder Description'],
                'Folder Created At': folder['Folder Created At'],
                'Folder Updated At': folder['Folder Updated At'],
                'Response ID': response['Response ID'],
                'Response Title': response['Response Title'],
                'Response Content': response['Response Content'],
                'Response Created At': response['Response Created At'],
                'Response Updated At': response['Response Updated At']
            })

print(f"All canned response folders and their responses have been exported to {csv_file}.")