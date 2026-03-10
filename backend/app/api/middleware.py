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
            os_family=user_agent.os.family
        ):
            logger.info("Request started")
            
            try:
                response = await call_next(request)
                
                process_time_ms = (time.perf_counter() - start_time) * 1000
                logger.info(
                    "Request completed",
                    extra={"status_code": response.status_code, "process_time_ms": round(process_time_ms, 2)}
                )
                
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Process-Time"] = str(process_time_ms)
                return response
                
            except Exception as e:
                process_time_ms = (time.perf_counter() - start_time) * 1000
                logger.exception(
                    "Request failed with exception",
                    extra={"status_code": 500, "process_time_ms": round(process_time_ms, 2), "error": str(e)}
                )
                raise e
