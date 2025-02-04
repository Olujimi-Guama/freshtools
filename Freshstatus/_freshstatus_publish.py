import requests
import os
import json
import pytz
import tzlocal
from datetime import datetime, timedelta, timezone, time
from _freshstatus_api import is_debug_mode, is_dry_run_mode, make_api_request

# Global variables
os.environ['DEBUG'] = 'True'
os.environ['DRY_RUN'] = 'True'

def get_user_timezone():
    """Get the user's local timezone. Default to EST if not detected."""
    try:
        return tzlocal.get_localzone()
    except Exception:
        return pytz.timezone('America/New_York')

def get_next_day(day_of_week, start_time, end_time):
    """Get the date of the next specified day in the user's local timezone."""
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_index = days_of_week.index(day_of_week)
    
    tz = pytz.timezone('America/New_York')
    today = datetime.now(tz)
    
    if today.weekday() == day_index:  # Check if today is the specified day
        next_day = today + timedelta(days=7)
    else:
        next_day = today + timedelta((day_index - today.weekday()) % 7)
    
    # Set the start and end times in the user's local timezone
    start_time_local = next_day.replace(hour=start_time.hour, minute=start_time.minute, second=0, microsecond=0)
    end_time_local = next_day.replace(hour=end_time.hour, minute=end_time.minute, second=0, microsecond=0)
    
    # Convert the start and end times to ISO 8601 UTC format
    start_time_iso = start_time_local.astimezone(pytz.utc).isoformat()
    end_time_iso = end_time_local.astimezone(pytz.utc).isoformat()
    
    return start_time_iso, end_time_iso

def convert_to_iso_format(date_str, time_str, tz_name=None):
    """Convert a date and time string to ISO 8601 format in UTC."""
    tz = pytz.timezone(tz_name) if tz_name else get_user_timezone()
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %I:%M %p")
    dt = dt.replace(tzinfo=tz)
    dt = dt.astimezone(pytz.utc)
    return dt.isoformat()

def convert_from_iso_format(iso_str, tz_name=None):
    """Convert an ISO 8601 formatted string to a date and time string in the user's local timezone."""
    tz = pytz.timezone(tz_name) if tz_name else get_user_timezone()
    dt = datetime.fromisoformat(iso_str)
    dt = dt.astimezone(tz)
    return dt.strftime("%Y-%m-%d %I:%M %p")

def prompt_for_times():
    day_of_week = 'Sunday'
    start_time = time(6, 0)  # 06:00 AM
    end_time = time(12, 0)   # 12:00 PM
    tzEST = pytz.timezone('America/New_York')

    start_iso, end_iso = get_next_day(day_of_week, start_time, end_time)

    # Convert ISO 8601 UTC to local timezone for display
    start_local = convert_from_iso_format(start_iso)
    end_local = convert_from_iso_format(end_iso)

    # Convert ISO 8601 UTC to EST for server values
    start_server = convert_from_iso_format(start_iso, tz_name='America/New_York')
    end_server = convert_from_iso_format(end_iso, tz_name='America/New_York')

    start_time_input_date = input(f"Enter start date (default {start_local.split()[0]}): ")
    mssg = [
        f"Enter start time (default ",
        f"{start_server.split()[1]} {start_server.split()[2]} EST, " if get_user_timezone() is not tzEST else "",
        f"{start_local.split()[1]} {start_local.split()[2]} local): " ]
    start_time_input_time = input(''.join(mssg))
    end_time_input_date = input(f"Enter end date (default {end_local.split()[0]}): ")
    mssg = [
        f"Enter end time (default ",
        f"{end_server.split()[1]} {end_server.split()[2]} EST, " if get_user_timezone() is not tzEST else "",
        f"{end_local.split()[1]} {end_local.split()[2]} local): " ]
    end_time_input_time = input(''.join(mssg))

    start_date = start_time_input_date if start_time_input_date else start_local.split()[0]
    start_time = start_time_input_time if start_time_input_time else f"{start_local.split()[1]} {start_local.split()[2]}"
    
    end_date = end_time_input_date if end_time_input_date else end_local.split()[0]
    end_time = end_time_input_time if end_time_input_time else f"{end_local.split()[1]} {end_local.split()[2]}"
    
    # Convert to ISO 8601 format in UTC
    start_iso = convert_to_iso_format(start_date, start_time)
    end_iso = convert_to_iso_format(end_date, end_time)
    
    return start_iso, end_iso

def get_webhook_url(acct: str, team_name: str) -> str:
    """Read the webhook URL for the specified team from the JSON file."""
    
    print(f"Getting webhook for account: {acct}, team: {team_name}")
    webhook_path = os.path.join(os.path.expanduser('~'), '.secrets', f'freshstatus_{acct}.webhook')
    
    try:
        with open(webhook_path, 'r') as file:
            webhooks = json.load(file)
        
        for webhook in webhooks:
            if webhook['teams_name'] == team_name:
                return webhook['teams_webhook']
        
        # If no matching team name is found
        raise ValueError(f"No webhook found for team: {team_name}")
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: Webhooks file '{webhook_path}' not found.")
    except json.JSONDecodeError:
        raise ValueError(f"Error: Failed to decode JSON from '{webhook_path}'.")

        
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
            print(f"The following account{'s' if len(removed_accounts) > 1 else ''} "
                  f"have been removed from this maintenance: {removed_accounts_str}")

        while True:
            # Prompt user to adjust default times or use next Sunday by default
            start_iso, end_iso = prompt_for_times()

            # Convert ISO 8601 UTC to local timezone for display
            start_local = convert_from_iso_format(start_iso)
            end_local = convert_from_iso_format(end_iso)

            start_server = convert_from_iso_format(start_iso, tz_name='America/New_York')
            end_server = convert_from_iso_format(end_iso, tz_name='America/New_York')

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
        summary_state_test += "AND " if is_dry_run_mode() and is_debug_mode() else ""
        summary_state_test += "DEBUG MODE ACTIVE!" if is_debug_mode() else "!"

        summary_message = (
            f"******* {summary_state_test} *******\n" if is_debug_mode() or is_dry_run_mode() else ""
        )
        summary_message += (
            f"\nSummary:\n"
            f"TRAX Release Version: {rel_ver}\n"
            f"Start Time: {start_server} (server), {start_local} (local)\n"
            f"End Time: {end_server} (server), {end_local} (local)\n"
            f"Accounts: {', '.join([template['account'][acct]['name'] for acct in accounts])}\n"
        )

        if 'teams_integrated' in template:
            
            import pymsteams
            
            datestamp = datetime.fromisoformat(start_iso)
            
            date = datestamp.strftime("%A, %b %d, %Y")
            time = datestamp.strftime("%I:%M %p").lower()

            date = date.replace(" 0", " ")
            time = time.lstrip("0")

            myteams = pymsteams.connectorcard(get_webhook_url(template['teams_integrated']['tenant_id'], template['teams_integrated']['teams_name']))
            tmssg = template['teams_integrated']['teams_message']
            tmssg['Title'] = tmssg['Title'].format(rel_ver=rel_ver)
            
            
            tmssg['Title'] = input(f"Enter the message to be sent to the Teams channel\n(default \"{tmssg['Title']}\"): ") or tmssg['Title']
            tmssg['Deployment Status'] = input(f"Enter the deployment status\n(default \"{tmssg['Deployment Status']}\"): ") or tmssg['Deployment Status']
            tmssg['Development Resource'] = input(f"Enter the development resource\n(default \"{tmssg['Development Resource']}\"): ") or tmssg['Development Resource']
            tmssg['QC Resources'] = input(f"Enter the QC resources\n(default \"{tmssg['QC Resources']}\"): ") or tmssg['QC Resources']    
            tmssg['Notes'] = input(f"Enter any additional notes\n(default \"{tmssg['Notes']}\"): ") or tmssg['Notes']
            
            myteams.title(f"{tmssg['Title']}")
            myteams.text( 
                f"Release: **{rel_ver}**<br>"
                f"Deployment Status: **{tmssg['Deployment Status']}**<br>" 
                f"Deployment Date: **{date}**<br>"
                f"Time: **{time}**<br>"
                f"Development Resource: **{tmssg['Development Resource']}**<br>"
                f"QC Resources: **{tmssg['QC Resources']}**<br><br>"
                f"{tmssg['Notes']}<br>"                
                )
            
            summary_message += f"Teams Channel: {template['teams_integrated']['teams_name']}\n"
            summary_message += f"Teams Message: {tmssg['Title']}\n"
            summary_message += f"Deployment Status: {tmssg['Deployment Status']}\n"
            summary_message += f"Development Resource: {tmssg['Development Resource']}\n"
            summary_message += f"QC Resources: {tmssg['QC Resources']}\n"
            summary_message += f"Notes: {tmssg['Notes']}\n"
            
        else:
            summary_message += f"Teams Channel: None configured\n"

        
        print(summary_message)


        confirm_choice = input("Do you want to proceed with posting this maintenance? (yes/no): ").strip().lower()
        if confirm_choice != 'yes':
            print("Maintenance posting cancelled.")
            return
        
        if is_debug_mode(): print(myteams.payload)
        if not is_dry_run_mode: 
            myteams.send()
        
        # Loop through the remaining accounts and post the maintenance
        for acct in accounts:
             
            if 'account' not in template or acct not in template['account']:
                print(f"Error: A template is not available for the account '{acct}'. Please check the account name and try again.")
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
                # Send the POST request using make_api_request
                response = make_api_request(resource='maintenance/', mode='POST', acct=acct, payload=payload)

                # Print the response
                if response.status_code in [200, 201]:
                    print(f"Scheduled maintenance created successfully for account '{acct}'!")
                else:
                    print(f"Failed to create scheduled maintenance for account '{acct}'. Status code: {response.status_code}")
                    print(response.text)

        print("Maintenance posting completed.")

    except requests.exceptions.RequestException as e:
        print(f"Error: An error occurred while making the request. Details: {e}")
    except json.JSONDecodeError:
        print("Error: Failed to decode the JSON response. Please check the API response format.")
    except Exception as e:
        print(f"Error: An unexpected error occurred. Details: {e}")

if __name__ == "__main__":
    create_maintenance()