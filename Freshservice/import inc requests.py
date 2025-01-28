import requests
import json

# Define the API key and domain
api_key = '[redacted]'
domain = 'hts-fs-sandbox'
headers = {'Content-Type': 'application/json'}

# Function to fetch ticket details
def fetch_ticket(ticket_id):
    ticket_url = f'https://{domain}.freshservice.com/api/v2/ticket_form_fields?workspace_id=1'
    response = requests.get(ticket_url, headers=headers, auth=(api_key, 'X'))
    
    # Check if the response status code is 200 (OK)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch ticket details. Status code: {response.status_code}, Response: {response.text}")
        return None

# Fetch ticket details for ticket ID 20
ticket_id = 115
ticket_details = fetch_ticket(ticket_id)

# Print the ticket details if the fetch was successful
if ticket_details:
    print(json.dumps(ticket_details, indent=4))