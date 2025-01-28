import requests
from collections import defaultdict

def get_services(auth):
    url = 'https://public-api.freshstatus.io/api/v1/services/'
    headers = {'Content-Type': 'application/json'}

    response = requests.get(url, headers=headers, auth=auth)

    if response.status_code == 200:
        services = response.json().get('results', [])
        return services
    else:
        print(f"Failed to retrieve services. Status code: {response.status_code}")
        print("Response:", response.text)
        return None

if __name__ == "__main__":
    auth = ('[redacted]', 'hts-fs-sandbox-my-team.status')
    services = get_services(auth)
    
    if services:
        grouped_services = defaultdict(list)
        for service in services:
            group_name = service['group']['name']
            grouped_services[group_name].append(service)
        
        for group, services in grouped_services.items():
            print(f"Service Group: {group}")
            for service in services:
                print(f"  Service Name: {service['name']}, Status: {service['display_options']['uptime_history_enabled']}")