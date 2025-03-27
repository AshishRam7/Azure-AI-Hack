import fastmcp
from msgraph_core import GraphClient
import asyncio
from typing import List, Dict, Optional
from pydantic import BaseModel
from azure.identity import ClientSecretCredential

class EmailConfig(BaseModel):
    tenant_id: str
    client_id: str
    client_secret: str
    user_email: str

class EmailMCPServer:
    def __init__(self, config: EmailConfig):
        # Azure AD authentication
        self.credentials = ClientSecretCredential(
            tenant_id=config.tenant_id,
            client_id=config.client_id,
            client_secret=config.client_secret
        )
        
        # Microsoft Graph Client
        self.graph_client = GraphClient(credential=self.credentials)
        self.user_email = config.user_email

    async def list_mail_folders(self) -> List[Dict]:
        """
        List all mail folders for the user
        """
        endpoint = f'/users/{self.user_email}/mailFolders'
        response = await self.graph_client.get(endpoint)
        return response.json().get('value', [])

    async def list_messages(self, folder_id: Optional[str] = None, filter_query: Optional[str] = None) -> List[Dict]:
        """
        List messages, optionally filtered by folder and additional query
        """
        if folder_id:
            endpoint = f'/users/{self.user_email}/mailFolders/{folder_id}/messages'
        else:
            endpoint = f'/users/{self.user_email}/messages'
        
        # Add optional filtering
        if filter_query:
            endpoint += f'?$filter={filter_query}'
        
        response = await self.graph_client.get(endpoint)
        return response.json().get('value', [])

    async def send_email(self, to: List[str], subject: str, body: str) -> Dict:
        """
        Send an email
        """
        endpoint = f'/users/{self.user_email}/sendMail'
        message_body = {
            'message': {
                'subject': subject,
                'body': {
                    'contentType': 'Text',
                    'content': body
                },
                'toRecipients': [{'emailAddress': {'address': recipient}} for recipient in to]
            }
        }
        
        response = await self.graph_client.post(endpoint, json=message_body)
        return response.json()

    async def create_mail_rule(self, display_name: str, conditions: Dict, actions: Dict) -> Dict:
        """
        Create a new mail rule
        """
        endpoint = f'/users/{self.user_email}/mailRules'
        rule_body = {
            'displayName': display_name,
            'sequence': 1,
            'conditions': conditions,
            'actions': actions
        }
        
        response = await self.graph_client.post(endpoint, json=rule_body)
        return response.json()

    async def manage_attachments(self, message_id: str, action: str = 'list', attachment_data: Optional[Dict] = None) -> List[Dict]:
        """
        Manage attachments for a specific message
        Supports: list, add, delete
        """
        base_endpoint = f'/users/{self.user_email}/messages/{message_id}/attachments'
        
        if action == 'list':
            response = await self.graph_client.get(base_endpoint)
            return response.json().get('value', [])
        elif action == 'add':
            if not attachment_data:
                raise ValueError("Attachment data required for add action")
            response = await self.graph_client.post(base_endpoint, json=attachment_data)
            return [response.json()]
        elif action == 'delete':
            if not attachment_data or 'attachment_id' not in attachment_data:
                raise ValueError("Attachment ID required for delete action")
            delete_endpoint = f'{base_endpoint}/{attachment_data["attachment_id"]}'
            response = await self.graph_client.delete(delete_endpoint)
            return []
        else:
            raise ValueError(f"Unsupported action: {action}")

# FastMCP Server Setup
def create_email_mcp_server(config: EmailConfig):
    """
    Create an MCP server for email management
    """
    server = EmailMCPServer(config)
    
    @fastmcp.action
    async def list_folders():
        """List all email folders"""
        return await server.list_mail_folders()
    
    @fastmcp.action
    async def get_messages(folder_id: Optional[str] = None, filter: Optional[str] = None):
        """Get messages, optionally filtered"""
        return await server.list_messages(folder_id, filter)
    
    @fastmcp.action
    async def send_email(to: List[str], subject: str, body: str):
        """Send an email"""
        return await server.send_email(to, subject, body)
    
    @fastmcp.action
    async def create_rule(display_name: str, conditions: Dict, actions: Dict):
        """Create an email rule"""
        return await server.create_mail_rule(display_name, conditions, actions)
    
    @fastmcp.action
    async def manage_email_attachments(message_id: str, action: str = 'list', attachment_data: Optional[Dict] = None):
        """Manage email attachments"""
        return await server.manage_attachments(message_id, action, attachment_data)
    
    return server

# Example Usage
async def main():
    # Configuration (replace with your actual Azure AD and Graph API credentials)
    config = EmailConfig(
        tenant_id="b07476e5-2a4e-475f-b8f0-b5c62b0db5d8",
        client_id="d11f65bd-95f9-4e11-8bbf-875089d92829",
        client_secret="Gm_8Q~zOQD5O63ikfVBBxFlAKpkd5nDQ6TWE2bbv",
        user_email='outlook_20C97BFA81D4DC09@outlook.com'
    )
    
    # Create MCP Server
    email_server = create_email_mcp_server(config)
    
    # Start the server
    await fastmcp.serve(email_server)

if __name__ == '__main__':
    asyncio.run(main())