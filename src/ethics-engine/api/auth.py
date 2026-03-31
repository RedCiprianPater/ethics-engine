"""Authentication utilities."""

from fastapi import HTTPException, Header
from typing import Optional


async def verify_api_key(authorization: Optional[str] = Header(None)) -> str:
    """
    Verify API key from Authorization header.
    
    Args:
        authorization: Authorization header value (Bearer token)
        
    Returns:
        API key if valid
        
    Raises:
        HTTPException: If authentication fails
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization format")
    
    api_key = authorization[7:]  # Remove "Bearer "
    
    # TODO: Validate against database
    if not api_key or len(api_key) < 10:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key


async def get_agent_id(x_agent_id: Optional[str] = Header(None)) -> str:
    """
    Get agent ID from header.
    
    Args:
        x_agent_id: X-Agent-ID header value
        
    Returns:
        Agent ID
        
    Raises:
        HTTPException: If agent ID is missing
    """
    if not x_agent_id:
        raise HTTPException(status_code=400, detail="Missing X-Agent-ID header")
    
    return x_agent_id
