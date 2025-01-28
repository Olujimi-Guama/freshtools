import requests
import json

# Define the API key and domain
api_key = '[redacted]'
domain = 'hts'
headers = {'Content-Type': 'application/json'}

# Function to fetch workspaces
def fetch_workspaces():
    workspaces_url = f'https://{domain}.freshservice.com/api/v2/workspaces'
    response = requests.get(workspaces_url, headers=headers, auth=(api_key, 'X'))
    return json.loads(response.text)

# Fetch workspaces
workspaces = fetch_workspaces()

# Print the list of workspaces
for workspace in workspaces['workspaces']:
    print(f"Workspace ID: {workspace['id']}, Workspace Name: {workspace['name']}")