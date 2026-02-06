"""
Router for Databricks Agent Assistant integration.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import requests

router = APIRouter(prefix="/api/agent", tags=["agent"])


class Message(BaseModel):
    role: str
    content: str


class AgentRequest(BaseModel):
    messages: List[Message]


@router.post("/chat")
async def chat_with_agent(request: AgentRequest):
    """
    Proxy requests to the Databricks Agent endpoint.
    Uses Databricks Agent format with input array.
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        agent_endpoint = os.getenv("DATABRICKS_AGENT_ENDPOINT")
        databricks_token = os.getenv("DATABRICKS_TOKEN")
        
        if not agent_endpoint:
            raise HTTPException(
                status_code=500, 
                detail="DATABRICKS_AGENT_ENDPOINT not configured"
            )
        
        # For development, we'll use client credentials to get a token
        # In production (Databricks Apps), this would use the app's identity
        if not databricks_token:
            # Get token using OAuth client credentials
            client_id = os.getenv("DATABRICKS_CLIENT_ID")
            client_secret = os.getenv("DATABRICKS_CLIENT_SECRET")
            databricks_host = os.getenv("DATABRICKS_HOST")
            
            if not all([client_id, client_secret, databricks_host]):
                raise HTTPException(
                    status_code=500,
                    detail="Databricks credentials not configured"
                )
            
            # Get OAuth token
            token_url = f"{databricks_host}/oidc/v1/token"
            token_response = requests.post(
                token_url,
                data={
                    "grant_type": "client_credentials",
                    "scope": "all-apis"
                },
                auth=(client_id, client_secret)
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to get auth token: {token_response.text}"
                )
            
            databricks_token = token_response.json().get("access_token")
        
        # Prepare request in Databricks Agent format
        # Convert messages to input array format
        agent_request = {
            "input": [{"role": msg.role, "content": msg.content} for msg in request.messages]
        }
        
        logger.info(f"Sending request to agent: {agent_request}")
        
        # Call agent endpoint
        headers = {
            "Authorization": f"Bearer {databricks_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            agent_endpoint,
            headers=headers,
            json=agent_request,
            timeout=120  # Increased timeout to 2 minutes for complex agent queries
        )
        
        if response.status_code != 200:
            logger.error(f"Agent request failed: {response.status_code} - {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Agent request failed: {response.text}"
            )
        
        result = response.json()
        logger.info(f"Agent response: {result}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
