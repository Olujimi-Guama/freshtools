'''
This script will:

- Prompt the user for the TRAX Release version being scheduled.
- Load a JSON template file containing the maintenance configuration.
- List the accounts in the template and prompt the user to select accounts to remove.
- Ensure at least one account remains after removal.
- Prompt the user to adjust the default start and end times for the maintenance window.
- Validate that the end time is after the start time.
- Display a summary of the maintenance details, including the message, start and end times, and account names.
- Ask for final confirmation to post the maintenance or cancel.
- Construct the path to the API key file using the account name.
- Read the API key from the specified path.
- Send a POST request to create the scheduled maintenance for the remaining accounts.

The script includes error handling for invalid account names, missing API key files, and issues with making the API request.

Dependencies:
- requests: To make HTTP requests to the Freshstatus API.
- os: To handle file paths and environment variables.
- json: To load and parse the JSON template file.
- datetime: To handle date and time operations.
- timezone: To handle timezone conversions.

This script was written with assistance from Microsoft Copilot.

nestor.sanchez@kore.solutions
20250112
'''

import requests
import os
import json
from datetime import datetime, timedelta, timezone
from _freshstatus_api import is_debug_mode, is_dry_run_mode

# Set the DEBUG environment variable to 'True'
os.environ['DEBUG'] = 'True'
# os.environ['DRY_RUN'] = 'True'

def check_account_exists(acct, template):
    if template and 'account' in template and acct in template['account']:
        return True
    else:
        print(f"Error: A template is not available for the account '{acct}'. Please check the account name and try again.")
        return False

def get_next_sunday():
    today = datetime.now(timezone(timedelta(hours=-5)))  # EST timezone
    next_sunday = today + timedelta((6 - today.weekday()) % 7)
    return next_sunday

def convert_to_iso_format(date_str, time_str):
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %I:%M %p")
    dt = dt.astimezone(timezone.utc)
    return dt.isoformat()

def prompt_for_times():
    next_sunday = get_next_sunday()
    default_start_time_est = next_sunday.replace(hour=6, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %I:%M %p")
    default_end_time_est = next_sunday.replace(hour=12, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %I:%M %p")

    start_time_input_date = input(f"Enter start date (default {default_start_time_est.split()[0]}): ")
    start_time_input_time = input(f"Enter start time (default {default_start_time_est.split()[1]} {default_start_time_est.split()[2]}) (all times in EST): ")

    end_time_input_date = input(f"Enter end date (default {default_end_time_est.split()[0]}): ")
    end_time_input_time = input(f"Enter end time (default {default_end_time_est.split()[1]} {default_end_time_est.split()[2]}) (all times in EST): ")

    start_date = start_time_input_date if start_time_input_date else default_start_time_est.split()[0]
    start_time = start_time_input_time if start_time_input_time else f"{default_start_time_est.split()[1]} {default_start_time_est.split()[2]}"

    end_date = end_time_input_date if end_time_input_date else default_end_time_est.split()[0]
    end_time = end_time_input_time if end_time_input_time else f"{default_end_time_est.split()[1]} {default_end_time_est.split()[2]}"

    return start_date, start_time, end_date, end_time

def create_maintenance():
    try:
        rel_ver = input("Enter the TRAX Release version being scheduled: ")

        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Check if the template file exists
        template_path = os.path.join(script_dir, 'Templates', 'fstatus_templates.json')
        if not os.path.exists(template_path):
            print("Error: Template file 'fstatus_templates.json' not found. Please ensure the file exists in the same directory.")
            return

        with open(template_path, 'r') as file:
            template = json.load(file)

        # List the accounts in the template and prompt user to select accounts to remove
        accounts = list(template['account'].keys())
        accounts_str = "\n".join([f"{i + 1}. {template['account'][account]['name']}" for i, account in enumerate(accounts)])
        print(f"The {template['type']} template \"{template['template_name']}\" is configured for the accounts:\n{accounts_str}")
        remove_indices = input("\nEnter the numbers associated with the accounts to remove, separated by commas (e.g., 1,3): ")
        remove_indices = [int(index.strip()) - 1 for index in remove_indices.split(",") if index.strip().isdigit()]

        # Check to prevent removing all accounts
        if len(remove_indices) >= len(accounts):
            print("Error: You cannot remove all accounts. Please leave at least one account.")
            return

        # Remove the selected accounts
        removed_accounts = []
        for index in sorted(remove_indices, reverse=True):
            if 0 <= index < len(accounts):
                removed_account = accounts.pop(index)
                removed_accounts.append(template['account'][removed_account]['name'])
        
        if removed_accounts:
            removed_accounts_str = ", ".join(removed_accounts)
            print(f"The following account{'s' if len(removed_accounts) > 1 else ''} have been removed from this \
                  maintenance: {removed_accounts_str}")

        while True:
            # Prompt user to adjust default times or use next Sunday by default
            start_date, start_time, end_date, end_time = prompt_for_times()

            start_iso = convert_to_iso_format(start_date, start_time)
            end_iso = convert_to_iso_format(end_date, end_time)

            # Validate that end time is after start time
            if end_iso <= start_iso:
                print("Error: End time entered cannot be earlier than set start time. Please enter valid times.")
                retry_choice = input("Would you like to retry entering the times? (yes/no): ").strip().lower()
                if retry_choice != 'yes':
                    return
            else:
                break

        # Display summary and ask for confirmation
        summary_state_test = "DRY RUN MODE ACTIVE " if is_dry_run_mode() else ""
        summary_state_test = f"{summary_state_test} AND " if is_dry_run_mode() and is_debug_mode() else ""
        summary_state_test = f"{summary_state_test} DEBUG MODE ACTIVE!" if is_debug_mode() else "!"
        summary_message = (
            f"******* {summary_state_test} *******\n"
            f"\nSummary:\n"
            f"TRAX Release Version: {rel_ver}\n"
            f"Start Time: {start_iso} (UTC)\n"
            f"End Time: {end_iso} (UTC)\n"
            f"Accounts: {', '.join([template['account'][acct]['name'] for acct in accounts])}\n"
        )
        print(summary_message)
        confirm_choice = input("Do you want to proceed with posting this maintenance? (yes/no): ").strip().lower()
        if confirm_choice != 'yes':
            print("Maintenance posting cancelled.")
            return

        # Construct the path to the API key file
        api_key_path = os.path.join(os.environ['USERPROFILE'], '.secrets', f'freshstatus_{accounts[0]}.key')
        
        # Read the API key from the file
        try:
            with open(api_key_path, 'r') as file:
                api_key = file.read().strip()
        except FileNotFoundError:
            print(f"Error: API key file not found at {api_key_path}. Please check the account name and try again.")
            return
            
        auth = (api_key, accounts[0])

        # Define the API endpoint
        url = 'https://public-api.freshstatus.io/api/v1/maintenance/'
        headers = {'Content-Type': 'application/json'}

        # Loop through the remaining accounts and post the maintenance
        for acct in accounts:
            if not check_account_exists(acct, template):
                continue

            # Define the payload using the template and account-specific details
            payload = {
                "title": ("[TEST]: " if is_debug_mode() else "") + template["title"].format(rel_ver=rel_ver),
                "description": template["description"].format(rel_ver=rel_ver),
                "start_time": start_iso,
                "end_time": end_iso,
                "is_auto_start": template["is_auto_start"],
                "is_auto_end": template["is_auto_end"],
                "is_private": True if is_debug_mode() else template["is_private"],
                "affected_components": template['account'][acct]['affected_components'],
                "notification_options": template["notification_options"] if not is_debug_mode() else { 
                    "send_notification": "false",
                    "send_tweet": "false",
                    "email_on_start": "false",
                    "email_on_complete": "false",
                    "email_before_day_hour": "false",
                    "email_before_one_hour": "false"
                },
                "maintenance_updates": template["maintenance_updates"]
            }

            # Add the array from template["account"][acct] to the payload
            payload.update(template["account"][acct])

            if is_dry_run_mode():
                # Display the payload in JSON format for debugging
                print("Debugging mode enabled. The payload is displayed below:")
                print(json.dumps(payload, indent=4))
            else:
                # Send the POST request
                response = requests.post(url, headers=headers, json=payload, auth=auth)

                # Print the response
                if response.status_code in [200, 201]:
                    print(f"Scheduled maintenance created successfully for account '{acct}'!")
                else:
                    print(f"Failed to create scheduled maintenance for account '{acct}'. Status code: {response.status_code}")
                    print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"Error: An error occurred while making the request. Details: {e}")
    except json.JSONDecodeError:
        print("Error: Failed to decode the JSON response. Please check the API response format.")
    except Exception as e:
        print(f"Error: An unexpected error occurred. Details: {e}")

if __name__ == "__main__":
    create_maintenance()