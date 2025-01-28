#
# Script: Freshstatus Service Fetcher
# Date: 20250119
# Author: Nestor Sanchez <nestor.sanchez@kore.solutions>
#
# Overview:
# This script fetches the groups and services from Freshstatus API for a given account name.
# It then saves the fetched data to a JSON file if the user chooses to do so.
#
# This script was written with assistance from Microsoft Copilot.


import os
import json
from datetime import datetime
from typing import Dict
from _freshstatus_api import make_api_request


def build_services_list(acct: str) -> Dict:
    """
    Fetches the groups and services from Freshstatus API for the given account name.

    Args:
        acct (str): Freshstatus account name.

    Returns:
        dict: A dictionary containing the fetched groups and services.
    """
    print("Fetching groups...")
    groups_response = make_api_request(resource='groups/', mode='GET', acct=acct)
    groups = groups_response.json()['results']

    print("Fetching services...")
    services_response = make_api_request(resource='services/', mode='GET', acct=acct)
    services = services_response.json()['results']

    return {"groups": groups, "services": services}


def save_services_to_file(services, filename):
    """
    Saves the services data to a JSON file.

    Args:
        services (dict): A dictionary containing the services data.
        filename (str): The name of the JSON file to save.
    """
    with open(filename, 'w') as file:
        json.dump(services, file, indent=4)


def main():
    """
    The main function of the script.
    """
    acct = input("Please enter your Freshstatus account name "
                 "(e.g., 'XYZ' if your Freshstatus URL is 'XYZ.freshstatus.io'): ")

    services = build_services_list(acct)
    print(json.dumps(services, indent=4))

    save_to_file = input("Would you like to save the information to a file? (yes/no): ").strip().lower()
    if save_to_file == 'yes':
        current_time = datetime.now().strftime("%Y%m%d%H%M")
        filename = f'fstatus_{acct}_services_backup-{current_time}.json'
        save_services_to_file(services, filename)
        print(f"Services exported to {filename}")


if __name__ == "__main__":
    main()
    print("Script has completed.")