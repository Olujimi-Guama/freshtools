import os
import json
import requests
from typing import Optional, Tuple, Dict

class DryRunModeError(Exception):
    pass

# Constants for HTTP methods
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'

def is_debug_mode() -> bool:
    """Check if the debug mode is enabled via environment variable."""
    return os.getenv('DEBUG', 'False').lower() in ['true', '1', 't', 'y', 'yes']

def is_dry_run_mode() -> bool:
    """Check if the dry-run mode is enabled via environment variable."""
    return os.getenv('DRY_RUN', 'False').lower() in ['true', '1', 't', 'y', 'yes']

def read_api_key(acct: str) -> str:
    """Read the API key from the file."""
    api_key_path = os.path.join(os.path.expanduser('~'), '.secrets', f'freshstatus_{acct}.key')
    with open(api_key_path, 'r') as file:
        return file.read().strip()

def validate_payload(payload: str) -> bool:
    """Validate if the payload is a valid JSON."""
    try:
        isinstance(payload, dict)
        return True
    except ValueError:
        return False

def check_account_exists(acct: str) -> bool:
    """Check if the given account exists in Freshstatus."""
    endpoint = 'https://public-api.freshstatus.io/api/v1/accounts'
    api_key = read_api_key(acct)
    headers = {'Authorization': f'Bearer {api_key}'}

    with requests.Session() as session:
        session.headers.update(headers)
        response = session.get(endpoint)
        if response.status_code == 200:
            accounts = response.json()
            for account in accounts:
                if account['name'] == acct:
                    return True
            return False
        else:
            print(f"Failed to retrieve accounts. Response status code: {response.status_code}")
            return False

def make_api_request(resource: Optional[str] = None, mode: Optional[str] = 'GET', 
                     acct: Optional[str] = None, payload: Optional[Dict] = None) -> requests.Response:
    endpoint = 'https://public-api.freshstatus.io/api/v1/'

    if acct is None:
        acct = input("Please enter your Freshstatus account name "
                     "(e.g., 'XYZ' if your Freshstatus URL is 'XYZ.freshstatus.io'): ")

    api_key = read_api_key(acct)
    headers = {'Content-Type': 'application/json'}
    auth = (api_key, acct)

    if mode in ['POST', 'PUT']:
        if payload is None or not validate_payload(payload):
            raise ValueError(f"Payload must be provided and valid JSON for {mode} mode.")
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dictionary")

    with requests.Session() as session:
        session.headers.update(headers)
        session.auth = auth

        if is_dry_run_mode() and mode in ['POST', 'PUT', 'DELETE']:
            raise DryRunModeError("API commands are disabled in dry-run mode. Please switch to live mode to execute this command.")
        
        try:
            response = session.request(
                method=mode,
                url=endpoint + resource,
                json=payload if payload else None
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response content: {response.content.decode('utf-8')}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error occurred: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"An error occurred: {req_err}")

            if is_debug_mode():
                print(f"Debug mode is ON. The request and response details are shown below.")
                print(f"Mode: {mode}")
                print(f"Endpoint: {endpoint}")
                print(f"Headers: {headers}")
                print(f"Auth: {auth}")
                if payload:
                    print(f"Payload: {payload}")
                print("Response status code:", response.status_code)
                print("Response content:", response.content.decode('utf-8'))

        return response

def get_service_components(auth: Tuple[str, str]) -> dict:
    api_key, account_name = auth
    url = 'https://public-api.freshstatus.io/api/v1/services'
    headers = {'Authorization': f'Bearer {api_key}'}
    with requests.Session() as session:
        session.headers.update(headers)
        response = session.get(url)
        response.raise_for_status()
        return response.json()

def create_group(auth: Tuple[str, str], group_name: str, parent_id: str) -> dict:
    api_key, account_name = auth
    url = 'https://public-api.freshstatus.io/api/v1/groups'
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    data = {'name': group_name, 'parent_id': parent_id}
    with requests.Session() as session:
        session.headers.update(headers)
        response = session.post(url, json=data)
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    print(f"DEBUG: {is_debug_mode()}")
    print(f"TEST: {is_dry_run_mode()}")

    groups = make_api_request(resource='groups/', mode=GET, acct="hts-texas")['results']
    print('Groups: \n', groups)
    services = make_api_request(resource='services/', mode=GET, acct="hts-texas")['results']
    print('Services: \n', services)
    print("Script has completed.")