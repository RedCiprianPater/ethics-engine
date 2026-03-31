"""Rate limiting utilities."""

import time
from typing import Dict, Tuple


class RateLimiter:
    """
    Simple in-memory rate limiter.
    
    For production, use Redis or similar distributed store.
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, list] = {}
    
    async def check(self, agent_id: str) -> bool:
        """
        Check if request is within rate limit.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if allowed, False if rate limited
        """
        now = time.time()
        
        # Get or create request history
        if agent_id not in self._requests:
            self._requests[agent_id] = []
        
        # Remove old requests outside window
        cutoff = now - self.window_seconds
        self._requests[agent_id] = [
            req_time for req_time in self._requests[agent_id]
            if req_time > cutoff
        ]
        
        # Check limit
        if len(self._requests[agent_id]) >= self.max_requests:
            return False
        
        # Record this request
        self._requests[agent_id].append(now)
        return True
    
    def get_status(self, agent_id: str) -> Tuple[int, int]:
        """
        Get rate limit status for an agent.
        
        Returns:
            Tuple of (remaining_requests, reset_time_seconds)
        """
        now = time.time()
        
        if agent_id not in self._requests:
            return self.max_requests, 0
        
        cutoff = now - self.window_seconds
        valid_requests = [
            req_time for req_time in self._requests[agent_id]
            if req_time > cutoff
        ]
        
        remaining = max(0, self.max_requests - len(valid_requests))
        
        if valid_requests:
            reset_time = int(self.window_seconds - (now - min(valid_requests)))
        else:
            reset_time = 0
        
        return remaining, reset_time
