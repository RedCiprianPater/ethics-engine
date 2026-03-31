"""Async client for Ethics Engine API."""

import httpx
from typing import Optional, List, Dict, Any, AsyncIterator
import json

from .schemas import EthicsRequest, EthicsResponse, CompareRequest, CompareResponse, FeedbackRequest
from .exceptions import (
    EthicsEngineException,
    AuthenticationError,
    RateLimitError,
    TimeoutException,
)


class EthicsEngineAsync:
    """
    Asynchronous client for the Ethics Engine API.
    
    Example:
        >>> async with EthicsEngineAsync(api_key="key", agent_id="robot_01") as engine:
        ...     response = await engine.resolve(scenario="Should I refuse?")
        ...     print(response.conclusion)
    """
    
    def __init__(
        self,
        api_key: str,
        agent_id: str,
        base_url: str = "https://api.nworobotics.cloud/ethics/v1",
        timeout: float = 30.0,
    ):
        """
        Initialize the async Ethics Engine client.
        
        Args:
            api_key: API authentication key
            agent_id: Unique identifier for this agent/robot
            base_url: Base URL for the Ethics Engine API
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.agent_id = agent_id
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "X-Agent-ID": agent_id,
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )
    
    async def resolve(
        self,
        scenario: str,
        context: Optional[Dict[str, Any]] = None,
        frameworks: Optional[List[str]] = None,
        return_reasoning: bool = True,
        mode: str = "reasoning",
    ) -> EthicsResponse:
        """Resolve an ethical scenario (async)."""
        request = EthicsRequest(
            scenario=scenario,
            context=context,
            frameworks=frameworks,
            return_reasoning=return_reasoning,
            mode=mode,
        )
        
        try:
            response = await self._client.post(
                f"{self.base_url}/resolve",
                json=request.model_dump(),
            )
            response.raise_for_status()
            return EthicsResponse(**response.json())
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif e.response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            else:
                raise EthicsEngineException(f"API error: {e.response.text}")
                
        except httpx.TimeoutException:
            raise TimeoutException(f"Request timed out after {self.timeout}s")
            
        except Exception as e:
            raise EthicsEngineException(f"Unexpected error: {e}")
    
    async def stream_reasoning(
        self,
        scenario: str,
        context: Optional[Dict[str, Any]] = None,
        frameworks: Optional[List[str]] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream reasoning steps in real-time.
        
        Yields:
            Dict with framework, text, and intermediate conclusions
        """
        request = EthicsRequest(
            scenario=scenario,
            context=context,
            frameworks=frameworks,
            return_reasoning=True,
            mode="reasoning",
        )
        
        try:
            async with self._client.stream(
                "POST",
                f"{self.base_url}/stream/reasoning",
                json=request.model_dump(),
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        yield data
                        
        except Exception as e:
            raise EthicsEngineException(f"Streaming error: {e}")
    
    async def compare(
        self,
        actions: List[str],
        scenario: str,
        context: Optional[Dict[str, Any]] = None,
        frameworks: Optional[List[str]] = None,
    ) -> CompareResponse:
        """Compare multiple actions (async)."""
        request = CompareRequest(
            actions=actions,
            scenario=scenario,
            context=context,
            frameworks=frameworks,
        )
        
        try:
            response = await self._client.post(
                f"{self.base_url}/compare",
                json=request.model_dump(),
            )
            response.raise_for_status()
            return CompareResponse(**response.json())
            
        except Exception as e:
            raise EthicsEngineException(f"Failed to compare: {e}")
    
    async def get_frameworks(self) -> List[Dict[str, Any]]:
        """Get available frameworks (async)."""
        try:
            response = await self._client.get(f"{self.base_url}/frameworks")
            response.raise_for_status()
            return response.json()["frameworks"]
            
        except Exception as e:
            raise EthicsEngineException(f"Failed to get frameworks: {e}")
    
    async def report_outcome(
        self,
        request_id: str,
        agent_decision: str,
        outcome: str,
        feedback: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Report outcome (async)."""
        request = FeedbackRequest(
            request_id=request_id,
            agent_decision=agent_decision,
            outcome=outcome,
            feedback=feedback,
        )
        
        try:
            response = await self._client.post(
                f"{self.base_url}/learn",
                json=request.model_dump(),
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            raise EthicsEngineException(f"Failed to report outcome: {e}")
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
