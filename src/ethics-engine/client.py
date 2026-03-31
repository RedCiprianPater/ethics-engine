"""Synchronous client for Ethics Engine API."""

import httpx
from typing import Optional, List, Dict, Any
import json

from .schemas import EthicsRequest, EthicsResponse, CompareRequest, CompareResponse, FeedbackRequest
from .exceptions import (
    EthicsEngineException,
    AuthenticationError,
    RateLimitError,
    TimeoutException,
)


class EthicsEngine:
    """
    Synchronous client for the Ethics Engine API.
    
    Example:
        >>> engine = EthicsEngine(api_key="your_key", agent_id="robot_01")
        >>> response = engine.resolve(
        ...     scenario="Should I refuse an unsafe command?",
        ...     context={"environment": "factory"}
        ... )
        >>> print(response.conclusion)
    """
    
    def __init__(
        self,
        api_key: str,
        agent_id: str,
        base_url: str = "https://api.nworobotics.cloud/ethics/v1",
        timeout: float = 30.0,
    ):
        """
        Initialize the Ethics Engine client.
        
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
        
        self._client = httpx.Client(
            headers={
                "Authorization": f"Bearer {api_key}",
                "X-Agent-ID": agent_id,
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )
    
    def resolve(
        self,
        scenario: str,
        context: Optional[Dict[str, Any]] = None,
        frameworks: Optional[List[str]] = None,
        return_reasoning: bool = True,
        mode: str = "reasoning",
    ) -> EthicsResponse:
        """
        Resolve an ethical scenario.
        
        Args:
            scenario: Description of the ethical dilemma
            context: Additional context (environment, urgency, etc.)
            frameworks: Specific frameworks to invoke (auto-select if None)
            return_reasoning: Whether to include full reasoning chain
            mode: "reasoning" for full analysis, "fast_decision" for quick response
            
        Returns:
            EthicsResponse with conclusion and reasoning
            
        Raises:
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit is exceeded
            TimeoutException: If request times out
            EthicsEngineException: For other errors
        """
        request = EthicsRequest(
            scenario=scenario,
            context=context,
            frameworks=frameworks,
            return_reasoning=return_reasoning,
            mode=mode,
        )
        
        try:
            response = self._client.post(
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
    
    def compare(
        self,
        actions: List[str],
        scenario: str,
        context: Optional[Dict[str, Any]] = None,
        frameworks: Optional[List[str]] = None,
    ) -> CompareResponse:
        """
        Compare multiple actions against ethical frameworks.
        
        Args:
            actions: List of action descriptions to compare
            scenario: Context for the comparison
            context: Additional context
            frameworks: Specific frameworks to use
            
        Returns:
            CompareResponse with comparison results
        """
        request = CompareRequest(
            actions=actions,
            scenario=scenario,
            context=context,
            frameworks=frameworks,
        )
        
        try:
            response = self._client.post(
                f"{self.base_url}/compare",
                json=request.model_dump(),
            )
            response.raise_for_status()
            return CompareResponse(**response.json())
            
        except httpx.HTTPStatusError as e:
            self._handle_error(e)
            raise
            
        except Exception as e:
            raise EthicsEngineException(f"Unexpected error: {e}")
    
    def get_frameworks(self) -> List[Dict[str, Any]]:
        """
        Get list of available ethical frameworks.
        
        Returns:
            List of framework information dictionaries
        """
        try:
            response = self._client.get(f"{self.base_url}/frameworks")
            response.raise_for_status()
            return response.json()["frameworks"]
            
        except Exception as e:
            raise EthicsEngineException(f"Failed to get frameworks: {e}")
    
    def report_outcome(
        self,
        request_id: str,
        agent_decision: str,
        outcome: str,
        feedback: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Report the outcome of a decision for continuous learning.
        
        Args:
            request_id: ID of the original ethics request
            agent_decision: What decision was made
            outcome: What actually happened
            feedback: Optional human feedback
            
        Returns:
            Confirmation response
        """
        request = FeedbackRequest(
            request_id=request_id,
            agent_decision=agent_decision,
            outcome=outcome,
            feedback=feedback,
        )
        
        try:
            response = self._client.post(
                f"{self.base_url}/learn",
                json=request.model_dump(),
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            raise EthicsEngineException(f"Failed to report outcome: {e}")
    
    def _handle_error(self, error: httpx.HTTPStatusError) -> None:
        """Handle HTTP errors."""
        if error.response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif error.response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        else:
            raise EthicsEngineException(f"API error: {error.response.text}")
    
    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
