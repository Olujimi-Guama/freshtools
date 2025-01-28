import os
import sys
import json
from typing import Dict, Optional
from _freshstatus_api import make_api_request, is_debug_mode, validate_payload
from _freshstatus_fetch import build_services_list

# os.environ['DEBUG'] = 'True'

def read_backup_file(file_path: str) -> Dict:
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Backup file not found at {file_path}. Exiting script.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from backup file at {file_path}. Exiting script.")
        sys.exit(1)

from typing import Dict

def compare_lists(target_data: Dict, backup_data: Dict) -> Dict:
    """
    Compare two dictionaries representing target data and backup data.
    Returns a dictionary containing the differences between the two datasets.

    Args:
        target_data (Dict): The target data dictionary.
        backup_data (Dict): The backup data dictionary.

    Returns:
        Dict: A dictionary containing the differences between the target and backup data.
            The 'groups' key contains a list of differences in the groups.
            The 'services' key contains a list of differences in the services.
    """
    differences = {'groups': [], 'services': []}

    target_groups = target_data['groups']
    backup_groups = backup_data['groups']
    target_services = target_data['services']
    backup_services = backup_data['services']

    # Compare groups in target and backup data
    for group in target_groups:
        group['parent_name'] = next(({'name': g['name'], 'id': g['id']} for g in target_groups if g['id'] == group['parent']), None)

    for group in backup_groups:
        if group['name'] not in [g['name'] for g in target_groups]:
            group['exist_in_server'] = None
            if group['parent'] is not None and group['parent'] in [g['id'] for g in backup_groups]:
                group['parent_name'] = next({'name': g['name'], 'id': g['id']} for g in backup_groups if g['id'] == group['parent'])
            else:
                group['parent_name'] = None
        else:
            group['exist_in_server'] = next(g['id'] for g in target_groups if g['name'] == group['name'])

    differences['groups'] = backup_groups

    # Compare services in target and backup data
    for service in backup_services:
        if 'group' in service and service['group']:
            for group in differences['groups']:
                if group['id'] == service['group']['id'] and 'exist_in_server' in group:
                    service['group']['id'] = group['exist_in_server']
                    break

        service['exist_in_server'] = next(
            (s['id'] for s in target_services if s['name'] == service['name'] and 'group' in s and 'group' in service and s['group']['name'] == service['group']['name']),
            None
        )

    differences['services'] = backup_services

    return differences

def update_group_info(service, target_services, backup_groups):
    if service['group']:
        group_info = next(
            (g for g in target_services if 'group' in g and g['group']['name'] == service['group']['name']),
            None
        )
        if group_info:
            service['group']['id'] = group_info['group']['id']
        else:
            service['group']['id'] = next(g['id'] for g in backup_groups if g['name'] == service['group']['name'])

def process_services(data, acct):
    resource = 'services/'

    for item in data['services']:
        payload = {
            'name': item['name'],
            'description': item['description'],
            'order': item['order'],
            'group': item['group']['id'],
            'display_options': item['display_options']
        }

        response = make_api_request(resource, 'POST', acct=acct, payload=payload)

        if response.status_code == 201:
            item['id'] = response.json()['id']
            item['group']['id'] = response.json()['group']['id']
            item['group']['name'] = response.json()['group']['name']
            item['group']['parent'] = response.json()['group']['parent']
            item['group']['order'] = response.json()['group']['order']
        else:
            handle_http_error(response)

    return data

def handle_http_error(response):
    print(f"HTTP error occurred: {response.status_code} {response.reason}")
    print(f"Response content: {response.content.decode('utf-8')}")
    sys.exit(1)

def send_it(data: Dict, acct: str) -> Dict:
    if is_debug_mode():
        print('\n')
        print(f'Account: {acct} \ndata: {json.dumps(data, indent=4)}\n')

    if not validate_payload(data):
        print("Invalid data sent to the server. Exiting script.")
        if is_debug_mode():
            print('Please revise the data:\n', json.dumps(data, indent=4))
        sys.exit(1)

    resource = 'services/'
    for service in data['services']:
        response = make_api_request(resource, 'POST', acct=acct, payload=service)
        if response.status_code != 201:
            handle_http_error(response)

    return data

def main():
    if is_debug_mode():
        print("Debug mode is enabled.")
        acct = 'hts-texas'
        json_file_path = '~/fstatus_kore_services_backup-202501171023.json'
        json_file_path = os.path.expanduser(json_file_path)

    input_acct = input("Enter the Freshstatus account name: ")
    if not input_acct:
        print("Freshstatus account name is required. Exiting script.")
        sys.exit(1)
    acct = input_acct

    input_file = input("Enter the path to the JSON backup file: ")
    if not input_file:
        print("Path to the JSON backup file is required. Exiting script.")
        sys.exit(1)
    json_file_path = input_file
    
    data = read_backup_file(json_file_path)
    target_data = build_services_list(acct)
    differences = compare_lists(target_data, data)

    for service in differences['services']:
        update_group_info(service, target_data['services'], differences['groups'])

    send_it(differences, acct)

if __name__ == "__main__":
    main()