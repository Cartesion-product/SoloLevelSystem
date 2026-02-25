"""Request logging middleware with trace_id injection."""

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logger import get_logger, set_trace_id

logger = get_logger("app.middleware")

# Paths to skip body logging (binary uploads, health checks)
_SKIP_BODY_PATHS = {"/docs", "/openapi.json", "/redoc", "/favicon.ico"}
# Content types that are readable text
_TEXT_CONTENT_TYPES = {"application/json", "application/x-www-form-urlencoded", "text/plain"}
# Max body size to log (prevent logging huge payloads)
_MAX_BODY_LOG = 2048


class TraceMiddleware(BaseHTTPMiddleware):
    """Assign a trace_id to each request and log request/response details."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Generate & set trace_id
        trace_id = uuid.uuid4().hex[:12]
        set_trace_id(trace_id)

        # Attach to request state for downstream access
        request.state.trace_id = trace_id

        method = request.method
        path = request.url.path
        client = request.client.host if request.client else "-"

        start_time = time.perf_counter()

        # --- Log request ---
        body_text = await self._read_body(request)
        if body_text:
            logger.info(f">>> {method} {path} from {client} body={body_text}")
        else:
            logger.info(f">>> {method} {path} from {client}")

        # --- Execute ---
        try:
            response = await call_next(request)
        except Exception as exc:
            elapsed = (time.perf_counter() - start_time) * 1000
            logger.error(f"<<< {method} {path} 500 {elapsed:.1f}ms ERROR: {exc}", exc_info=True)
            raise

        elapsed = (time.perf_counter() - start_time) * 1000
        status_code = response.status_code

        if status_code >= 500:
            logger.error(f"<<< {method} {path} {status_code} {elapsed:.1f}ms")
        elif status_code >= 400:
            logger.warning(f"<<< {method} {path} {status_code} {elapsed:.1f}ms")
        else:
            logger.info(f"<<< {method} {path} {status_code} {elapsed:.1f}ms")

        # Inject trace_id into response header for frontend debugging
        response.headers["X-Trace-Id"] = trace_id
        return response

    @staticmethod
    async def _read_body(request: Request) -> str | None:
        """Read and return request body for logging (if applicable)."""
        if request.url.path in _SKIP_BODY_PATHS:
            return None
        if request.method in ("GET", "HEAD", "OPTIONS", "DELETE"):
            return None

        content_type = request.headers.get("content-type", "")

        # For multipart (file uploads), only log form fields, not file content
        if "multipart/form-data" in content_type:
            return "[multipart/form-data]"

        # For JSON / form / text bodies
        for ct in _TEXT_CONTENT_TYPES:
            if ct in content_type:
                body = await request.body()
                text = body.decode("utf-8", errors="replace")
                if len(text) > _MAX_BODY_LOG:
                    return text[:_MAX_BODY_LOG] + f"...({len(text)} bytes truncated)"
                return text

        return None
