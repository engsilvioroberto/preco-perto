import time
from collections import defaultdict
from fastapi import Request, HTTPException, status

class RateLimiter:
    def __init__(self):
        self.requests: dict[str, list[float]] = defaultdict(list)

    async def __call__(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < 60]

        limit = 20 if "/auth/" in request.url.path else 60

        if len(self.requests[client_ip]) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Muitas requisições. Tente novamente em instantes."
            )

        self.requests[client_ip].append(now)
        response = await call_next(request)
        return response
