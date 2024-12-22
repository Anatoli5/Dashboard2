import time
import asyncio
from typing import Optional, Dict, Any
import aiohttp
import streamlit as st
from datetime import datetime, timedelta
from functools import wraps

class RateLimiter:
    """Rate limiter for API requests"""
    
    def __init__(self, calls: int, period: int):
        self.calls = calls  # Number of calls allowed
        self.period = period  # Time period in seconds
        self.timestamps = []
    
    def is_allowed(self) -> bool:
        """Check if request is allowed under current rate limits"""
        now = time.time()
        # Remove timestamps older than the period
        self.timestamps = [ts for ts in self.timestamps if now - ts < self.period]
        
        if len(self.timestamps) < self.calls:
            self.timestamps.append(now)
            return True
        return False
    
    def wait_time(self) -> float:
        """Get time to wait before next request is allowed"""
        if self.is_allowed():
            return 0
        
        now = time.time()
        next_slot = self.timestamps[0] + self.period
        return max(0, next_slot - now)

class RequestManager:
    """Manages API requests with rate limiting and caching"""
    
    # Rate limits for different providers
    RATE_LIMITS = {
        'alpha_vantage': {'calls': 5, 'period': 60},  # 5 calls per minute
        'yahoo': {'calls': 2000, 'period': 3600}      # 2000 calls per hour
    }
    
    def __init__(self):
        self.rate_limiters = {
            provider: RateLimiter(limits['calls'], limits['period'])
            for provider, limits in self.RATE_LIMITS.items()
        }
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes default cache
    
    def set_cache_timeout(self, timeout: int):
        """Set cache timeout in seconds"""
        self.cache_timeout = timeout
    
    def _get_cache_key(self, url: str, params: Dict[str, Any]) -> str:
        """Generate cache key from URL and parameters"""
        param_str = '&'.join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"{url}?{param_str}"
    
    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if cached data is still valid"""
        return time.time() - timestamp < self.cache_timeout
    
    async def request(self, 
                     provider: str,
                     url: str,
                     params: Dict[str, Any],
                     method: str = 'GET',
                     use_cache: bool = True) -> Dict[str, Any]:
        """Make an API request with rate limiting and caching"""
        
        cache_key = self._get_cache_key(url, params)
        
        # Check cache first
        if use_cache and cache_key in self.cache:
            timestamp, data = self.cache[cache_key]
            if self._is_cache_valid(timestamp):
                return data
        
        # Apply rate limiting
        rate_limiter = self.rate_limiters.get(provider)
        if rate_limiter:
            wait_time = rate_limiter.wait_time()
            if wait_time > 0:
                st.info(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
                try:
                    await asyncio.sleep(wait_time)
                except asyncio.CancelledError:
                    # Handle cancellation gracefully
                    return {}
        
        # Make the request
        try:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.request(method, url, params=params, timeout=10) as response:
                        response.raise_for_status()
                        data = await response.json()
                        
                        # Cache the response
                        if use_cache:
                            self.cache[cache_key] = (time.time(), data)
                        
                        return data
                
                except asyncio.CancelledError:
                    # Handle cancellation gracefully
                    return {}
                except aiohttp.ClientError as e:
                    st.error(f"Request failed: {str(e)}")
                    raise
                
        except Exception as e:
            st.error(f"Request error: {str(e)}")
            return {}
    
    @staticmethod
    def get_instance() -> 'RequestManager':
        """Get or create RequestManager instance"""
        if 'request_manager' not in st.session_state:
            st.session_state.request_manager = RequestManager()
        return st.session_state.request_manager

def with_request_manager(f):
    """Decorator to inject RequestManager instance"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        request_manager = RequestManager.get_instance()
        return f(request_manager, *args, **kwargs)
    return wrapper 