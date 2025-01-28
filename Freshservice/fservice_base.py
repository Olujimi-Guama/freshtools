'''
This script will:

- Prompt the user for the Freshstatus account name.
- Check if the account exists.
- Construct the path to the API key file using the account name.
- Read the API key from the specified path.
- Retrieve all services and group them by their respective groups.
- Print the grouped services and components on the screen.

The script includes error handling for invalid account names, missing API key files, and issues with retrieving the services.

This script was written with assistance from Microsoft Copilot.

nestor.sanchez@kore.solutions
20230929
'''

import json
import requests
from collections import defaultdict
import os
import sys

# Global variable for debugging
DEBUG = 1

def get_services(auth):
    url = 'https://public-api.freshstatus.io/api/v1/services/'
    headers = {'Content-Type': 'application/json'}

    response = requests.get(url, headers=headers, auth=auth)

    if response.status_code == 200:
        services = response.json().get('results', [])
        return services, response
    else:
        print(f"Failed to retrieve services. Status code: {response.status_code}")
        print("Response:", response.text)
        return None, response

def check_account_exists(acct):
    url = f'https://{acct}.freshstatus.io'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True, response
        else:
            print(f"Account {acct} does not exist. Status code: {response.status_code}")
            return False, response
    except requests.exceptions.RequestException as e:
        print(f"Error checking account: {e}")
        return False, None

def main():
    # Prompt the user for the account name
    acct = input("Please enter your Freshstatus account name (e.g., 'XYZ' if your Freshstatus URL is 'XYZ.freshstatus.io'): ")
    
    # Check if the account exists
    account_exists, response = check_account_exists(acct)
    if not account_exists:
        sys.exit(1)
    
    # Construct the path to the API key file
    api_key_path = os.path.join(os.environ['USERPROFILE'], '.secrets', f'freshstatus_{acct}.key')
    
    # Read the API key from the file
    try:
        with open(api_key_path, 'r') as file:
            api_key = file.read().strip()
    except FileNotFoundError:
        print(f"API key file not found at {api_key_path}. Please check the account name and try again.")
        sys.exit(1)
        
    auth = (api_key, acct)
    
    services, response = get_services(auth)
    
    if services:
        grouped_services = defaultdict(lambda: {"group": None, "services": []})
        for service in services:
            group = service.get('group')
            if group:
                group_name = group['name']
                grouped_services[group_name]["group"] = group
                grouped_services[group_name]["services"].append(service)
            else:
                grouped_services['No Group']["services"].append(service)
        
        # Remove the group key from each service
        for group_name, group_data in grouped_services.items():
            for service in group_data["services"]:
                if "group" in service:
                    del service["group"]
        
        # Print the grouped services and components
        for group_name, group_data in grouped_services.items():
            print(f"Group: {group_name}")
            for service in group_data["services"]:
                print(f"  Service ID: {service['id']}")
                print(f"  Service Name: {service['name']}")
                print(f"  Service Status: {service.get('status', 'N/A')}")
                print(f"  Components: {service.get('components', [])}")
                print()

        # Summary message
        total_services = sum(len(group["services"]) for group in grouped_services.values())
        print(f"Total services: {total_services} grouped into {len(grouped_services)} groups.")
        
        # Server response debug
        if DEBUG:
            print("Response Status Code:", response.status_code)
            try:
                print("Response Content:", json.dumps(response.json(), indent=4))
            except json.JSONDecodeError:
                print("Response Content is not in JSON format")
        
if __name__ == "__main__":
    main()