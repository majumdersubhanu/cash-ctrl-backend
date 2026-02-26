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

        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()
        
        # Parse User Agent
        ua_string = request.headers.get("user-agent", "")
        user_agent = parse(ua_string)
        
        # Context bind
        with logger.contextualize(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            ip=request.client.host if request.client else "unknown",
            device_family=user_agent.device.family,
