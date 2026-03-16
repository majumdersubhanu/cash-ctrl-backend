import time
import logging

logger = logging.getLogger(__name__)

class PerformanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # Log if request takes more than 500ms
        if duration > 0.5:
            logger.warning(
                f"Slow Request: {request.method} {request.path} "
                f"took {duration:.2f}s (User: {request.user})"
            )
            
        return response
