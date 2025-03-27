import requests
import json
from config import TENANT_ID, CLIENT_ID, CLIENT_SECRET

def get_access_token():
    """
    Retrieve an access token using the OAuth 2.0 client credentials flow
    """
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'https://graph.microsoft.com/.default'
    }
    
    response = requests.post(token_url, data=token_data)
    
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        raise Exception(f"Failed to get token: {response.text}")