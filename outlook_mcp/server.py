import sys
import traceback
import requests
import json
from mcp.server.fastmcp import FastMCP
import dotenv
import os

class OutlookGraphAPI:
    def __init__(self, access_token):
        # Using v1.0 for most endpoints; the user profile will be fetched via beta.
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.beta_base_url = "https://graph.microsoft.com/beta"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def send_email(self, to_email, subject, body):
        """Send an email directly using Microsoft Graph API /sendMail endpoint."""
        endpoint = f"{self.base_url}/me/sendMail"
        payload = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": body
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": to_email
                        }
                    }
                ]
            }
        }
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            return "Email sent successfully"
        except requests.exceptions.RequestException as e:
            return f"Error sending email: {str(e)}"

    def create_event(self, subject, start_time, end_time, attendees=None):
        """Create a calendar event using Microsoft Graph API."""
        endpoint = f"{self.base_url}/me/events"
        payload = {
            "subject": subject,
            "start": {
                "dateTime": start_time,
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "UTC"
            }
        }
        
        if attendees:
            payload["attendees"] = [
                {"emailAddress": {"address": attendee}} for attendee in attendees
            ]
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            return "Event created successfully"
        except requests.exceptions.RequestException as e:
            return f"Error creating event: {str(e)}"

    def create_contact(self, display_name, email, phone=None):
        """Create a contact using Microsoft Graph API."""
        endpoint = f"{self.base_url}/me/contacts"
        payload = {
            "displayName": display_name,
            "emailAddresses": [{"address": email}]
        }
        
        if phone:
            payload["businessPhones"] = [phone]
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            return "Contact created successfully"
        except requests.exceptions.RequestException as e:
            return f"Error creating contact: {str(e)}"

    def create_task(self, task_list_id, title, due_date=None):
        """Create a task in a specific task list using Microsoft Graph API."""
        endpoint = f"{self.base_url}/me/todo/lists/{task_list_id}/tasks"
        payload = {
            "title": title
        }
        
        if due_date:
            payload["dueDateTime"] = {
                "dateTime": due_date,
                "timeZone": "UTC"
            }
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            return "Task created successfully"
        except requests.exceptions.RequestException as e:
            return f"Error creating task: {str(e)}"

    def get_my_mails(self, top=10):
        """Retrieve mail messages using Microsoft Graph API."""
        endpoint = f"{self.base_url}/me/messages?$top={top}"
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return f"Error retrieving mails: {str(e)}"

    def list_onedrive_items(self):
        """List OneDrive items using Microsoft Graph API."""
        endpoint = f"{self.base_url}/me/drive/root/children"
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return f"Error listing OneDrive items: {str(e)}"

    def get_user_profile(self):
        """Retrieve user profile details using Microsoft Graph API (beta endpoint)."""
        # Using the beta version to get profile details
        endpoint = f"{self.beta_base_url}/me/profile"
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return f"Error retrieving user profile: {str(e)}"

# Create an MCP server instance
mcp = FastMCP("OutlookServer")

# Load environment variables for the access token
dotenv.load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
outlook_api = OutlookGraphAPI(ACCESS_TOKEN)

@mcp.tool()
def send_email(to_email: str, subject: str, body: str):
    """Send an email using Microsoft Graph API."""
    return outlook_api.send_email(to_email, subject, body)

@mcp.tool()
def create_calendar_event(subject: str, start_time: str, end_time: str, attendees: list = None):
    """Create a calendar event using Microsoft Graph API."""
    return outlook_api.create_event(subject, start_time, end_time, attendees)

@mcp.tool()
def create_contact(display_name: str, email: str, phone: str = None):
    """Create a contact using Microsoft Graph API."""
    return outlook_api.create_contact(display_name, email, phone)

@mcp.tool()
def create_task(task_list_id: str, title: str, due_date: str = None):
    """Create a task in a specific task list using Microsoft Graph API."""
    return outlook_api.create_task(task_list_id, title, due_date)

@mcp.tool()
def get_my_mails(top: int = 10):
    """Retrieve mail messages using Microsoft Graph API."""
    return outlook_api.get_my_mails(top)

@mcp.tool()
def list_onedrive_items():
    """List OneDrive items using Microsoft Graph API."""
    return outlook_api.list_onedrive_items()

@mcp.tool()
def get_user_profile():
    """Retrieve user profile details using Microsoft Graph API (beta)."""
    return outlook_api.get_user_profile()

if __name__ == "__main__":
    try:
        print("Running MCP Server for Outlook...", file=sys.stderr)
        mcp.run(transport="stdio")
    except Exception as e:
        print(f"Fatal Error in MCP Server: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
