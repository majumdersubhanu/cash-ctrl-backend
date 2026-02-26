import time
import uuid

from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from user_agents import parse


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        
        # We don't want to log noise like health checks
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)
