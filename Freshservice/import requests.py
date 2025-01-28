import requests
import json

# Define the API key and domain
api_key = '[redacted]'
domain = 'hts'
headers = {'Content-Type': 'application/json'}

def fetch_article(s_term, user_email, page=1, per_page=10):
    # Define the URL for fetching the article
    article_url = f'https://{domain}.freshservice.com/api/v2/solutions/articles/search?search_term={s_term}&' if user_email == user_email else '' + f'&page={page}&per_page={per_page}'
    
    # Make the API request to fetch the article
    response = requests.get(article_url, headers=headers, auth=(api_key, 'X'))
    
    # Check if the request was successful
    if response.status_code == 200:
        article = json.loads(response.text)
        return article
    else:
        print(f"Failed to fetch article with search term '{s_term}'. Status code: {response.status_code}")
        return None

# Example usage
article_id = 4000027604  # Replace with the actual article ID
s_term = 'cisco vpn'
user_email = None
article = fetch_article(s_term, user_email, page=2, per_page=10)
if article:
    for item in article['articles']:
        item['description_text'] = 'shortened for brevity'
        item['description'] = 'shortened for brevity'
    print('Total articles found:', len(article['articles']))
    print(json.dumps(article, indent=4))
