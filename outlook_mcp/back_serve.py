from mcp.server.fastmcp import FastMCP
import requests
from token_management import get_access_token
from config import GRAPH_API_URL
import sys
import traceback

mcp = FastMCP("OutlookAssistant")

def graph_request(method, endpoint, data=None):
    """Universal method for Microsoft Graph API requests"""
    #token = get_access_token()
    headers = {
        'Authorization': 'Bearer EwBYBMl6BAAUBKgm8k1UswUNwklmy2v7U/S+1fEAAeUXbLZVWhu0EIQRP9enoWFRc8yd/MJ46eNpifSVSoR9RwTHFku6Xdgjs3yiW+bE7qrSMV5XMrArcdMOUaU8QM41sT3H1wzu8CgOjZO97lthFM60rsyhvpGUG67i2M4rl3mieZEW0AsAE44QZUW8nK1rR/0iJNJOpPdW5kLLuFdP9ANMmlBaSakV6xmBB4VLDNuryis/TQrxJNB/m0G1bURxxMBYn8d3CldBvKKQpfOyeqkMenR+K9gHdN0PajwQZc4BXvJSVt9SOIUW76TQbHTNV82q/drRBJps+3i45TB5yWUAGQXCOzpYy+OzUVP3rpruDcKtl29xixp3YORVtGUQZgAAEBd0BmVKowcT+BJWZlHdzEMgA2jLzuHyE4yJgttEHIjVNz08hFm4yMx6j2XQWlpLJ9hWEPGvH5P4AWVTz25xLmxJu61pBwGYvxrsKpidUut088JX8eNrwjox+qgeRaFOnQI4vWbmlUfjP98fDVQbw6FQxMON9l38K+Tvfcv2yCzG9OlmocH2dGemu6wpFMqRuCPGGAAM5nd2P+e5BdBPBDiOWhUvSiW3nimWYR0if6xwM7eb31TCL5PAcfAgjmLIyKFE4vyB1zqY1fzALlUoi/U7X5k1x5KVad1S4zh0aKiTRNUl27SgNmh84ztRT9Xj/keYaiEBhyl8C18bVRGqYrZW9eqstW7/4kzMdtJIFmt14Vebnnhy+I95+nnH1eBjq7g3tpm6D5lK2Zdbvx/+fQOwi6RJU9UxDzFA9+BxWn4oQJ+iooPQg6av+6CCgFP0RC/hbdmi+gaZOE6GrmXVovxJHpR8ZxH9TTHZogrOy4DxOWDcYUQreQdTpWCKYfTR6gASBpVUE+rIbt1uCCplB8blnFG2B9SgbmrzoPyg3JnQHG2bM8fgDgVgtg6s1oWcvhlvDZh4PwdebZMwn05CfUF39n6/oALm58h+gJ3BFAZqzFl/LbQETNuPPQI3uObRR3zPjwQba9SRkI2wCq6E6ot6Dy7af56GGtp8pCcwSncWpBFlUJ7gEYaDmfcVfvgqH4sDKch5v8LCUgUm45GRbqVBnXXixTq++VL0WWLjROr2MTB5F3bNLhV22vD9jclD5fsAycRnrlhWf5FXnGiquiNXym7sZ1G58wfN1eFeogFw4BJKgzOe5gXuLdMjdTlJE/Nq6hckGY6g57FObldZuT8KNBI9hYx+Usefb0jnVIGiFN7ixDOphGuwckL9CnWqZglfFRyBujm+abAAHdaybPDH25nj2OPj7kHytvGmKhJHN05Erniw4R3hyL2KQIoBDRjn1tqxkxPl3XOwi7TSud01imuL9burNsaGeg8OdViQwpmT8YpSZhTPcWrxoKo+Cta7OoU6kV0Oekj4a6d6/mUSclbyTYUTEhAcXvG6gwb4mzHq2l3ngBweR7cDeajsmT9MYgM=',
        'Content-Type': 'application/json'
    }
    
    full_url = f"https://graph.microsoft.com/v1.0/{endpoint}"
    
    if method == 'GET':
        response = requests.get(full_url, headers=headers)
    elif method == 'POST':
        response = requests.post(full_url, headers=headers, json=data)
    
    response.raise_for_status()
    return response.json()

@mcp.tool()
def list_emails(folder: str = 'inbox', limit: int = 10):
    """List recent emails from a specified folder"""
    endpoint = f"me/mailFolders/{folder}/messages?$top={limit}"
    return graph_request('GET', endpoint)

@mcp.tool()
def send_email(to: str, subject: str, body: str):
    """Send an email"""
    endpoint = "me/sendMail"
    email_data = {
        "message": {
            "subject": subject,
            "body": {"contentType": "Text", "content": body},
            "toRecipients": [{"emailAddress": {"address": to}}]
        }
    }
    return graph_request('POST', endpoint, data=email_data)

if __name__ == "__main__":
    try:
        print("Running MCP Server for Outlook...", file=sys.stderr)
        mcp.run(transport="stdio")
    except Exception as e:
        print(f"Fatal Error in MCP Server: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)