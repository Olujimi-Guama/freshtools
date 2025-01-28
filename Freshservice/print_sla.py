import requests
import json

# Define the API key and domain
api_key = '[redacted]'
domain = 'hts'
headers = {'Content-Type': 'application/json'}

# Function to fetch SLA policies
def fetch_sla_policies():
    sla_policies_url = f'https://{domain}.freshservice.com/api/v2/sla_policies?workspace_id=2'
    response = requests.get(sla_policies_url, headers=headers, auth=(api_key, 'X'))
    
    # Check if the response status code is 200 (OK)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch SLA policies. Status code: {response.status_code}, Response: {response.text}")
        return None

# Fetch SLA policies
sla_policies = fetch_sla_policies()

# Print the list of SLA policies if the fetch was successful
if sla_policies:
    for sla in sla_policies['sla_policies']:
        print(f"SLA ID: {sla['id']}, SLA Name: {sla['name']}")