import asyncio
import msal
import httpx
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

class MicrosoftGraphAssistant:
    def __init__(self, client_id: str, client_secret: str, tenant_id: str):
        """
        Initialize Microsoft Graph API client
        
        :param client_id: Azure AD application (client) ID
        :param client_secret: Client secret for the application
        :param tenant_id: Azure AD tenant ID
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        
        # Authentication context
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scopes = ["https://graph.microsoft.com/.default"]
        
        # Create confidential client application
        self.app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret
        )
    
    async def get_access_token(self) -> str:
        """
        Acquire access token for Microsoft Graph API
        
        :return: Access token string
        """
        result = self.app.acquire_token_silent(self.scopes, account=None)
        
        if not result:
            result = self.app.acquire_token_for_client(scopes=self.scopes)
        
        if "access_token" in result:
            return result["access_token"]
        else:
            raise HTTPException(
                status_code=401, 
                detail="Could not acquire access token"
            )
    
    async def call_graph_api(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a generic call to Microsoft Graph API
        
        :param method: HTTP method (GET, POST, etc.)
        :param endpoint: Graph API endpoint
        :param data: Optional request body
        :return: API response
        """
        token = await self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(endpoint, headers=headers)
            elif method.upper() == "POST":
                response = await client.post(endpoint, headers=headers, json=data)
            elif method.upper() == "PATCH":
                response = await client.patch(endpoint, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = await client.delete(endpoint, headers=headers)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            response.raise_for_status()
            return response.json()
    
    # Specific Microsoft Graph API method implementations
    async def list_users(self) -> Dict[str, Any]:
        """List all users in the organization"""
        return await self.call_graph_api(
            "GET", 
            "https://graph.microsoft.com/v1.0/users"
        )
    
    async def list_groups(self) -> Dict[str, Any]:
        """List all groups in the organization"""
        return await self.call_graph_api(
            "GET", 
            "https://graph.microsoft.com/v1.0/groups"
        )
    
    async def send_email(
        self, 
        recipient: str, 
        subject: str, 
        body: str
    ) -> Dict[str, Any]:
        """
        Send an email via Microsoft Graph API
        
        :param recipient: Email recipient
        :param subject: Email subject
        :param body: Email body
        :return: Send operation result
        """
        email_data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": body
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": recipient
                        }
                    }
                ]
            },
            "saveToSentItems": "true"
        }
        
        return await self.call_graph_api(
            "POST", 
            "https://graph.microsoft.com/v1.0/me/sendMail", 
            data=email_data
        )

# FastAPI Application Setup
app = FastAPI(title="Microsoft Graph API Control Server")

# Dependency to initialize Microsoft Graph Assistant
def get_graph_assistant():
    return MicrosoftGraphAssistant(
        client_id="d11f65bd-95f9-4e11-8bbf-875089d92829",
        client_secret="Gm_8Q~zOQD5O63ikfVBBxFlAKpkd5nDQ6TWE2bbv", 
        tenant_id="b07476e5-2a4e-475f-b8f0-b5c62b0db5d8"
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.get("/callback")
async def callback(code: str):
    """Callback endpoint for OAuth2 authorization code flow"""
    return {"code": code}

# API Endpoints
@app.get("/users")
async def list_users(
    graph_assistant: MicrosoftGraphAssistant = Depends(get_graph_assistant)
):
    """Endpoint to list all users"""
    return await graph_assistant.list_users()

@app.post("/send-email")
async def send_email(
    email_data: Dict[str, Any],
    graph_assistant: MicrosoftGraphAssistant = Depends(get_graph_assistant)
):
    """
    Endpoint to send an email using Microsoft Graph API payload structure
    
    Expected payload format:
    {
        "message": {
            "subject": "string",
            "body": {
                "contentType": "Text" | "HTML",
                "content": "string"
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": "recipient@example.com"
                    }
                }
            ]
        },
        "saveToSentItems": "true" | "false"
    }
    """
    try:
        # Validate basic structure
        if "message" not in email_data:
            raise HTTPException(
                status_code=400, 
                detail="Invalid email payload: 'message' key is required"
            )
        
        else:
            return await graph_assistant.call_graph_api(method="POST",endpoint="https://graph.microsoft.com/v1.0/me/sendMail",data=email_data)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to send email: {str(e)}"
        )

# Update the MicrosoftGraphAssistant class to support this more generic approach
async def send_email(
    self, 
    message_payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Send an email using the full Microsoft Graph API payload
    
    :param message_payload: Complete email payload
    :return: API response
    """
    return await self.call_graph_api(method="POST",endpoint="https://graph.microsoft.com/v1.0/me/sendMail",data=message_payload)
    

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)