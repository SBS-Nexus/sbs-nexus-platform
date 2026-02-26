import uuid
from typing import Callable

from starlette.types import ASGIApp, Receive, Scope, Send


class CorrelationIdMiddleware:
    def __init__(self, app: ASGIApp, header_name: str = "X-Correlation-ID") -> None:
        self.app = app
        self.header_name = header_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Header auslesen oder neue ID generieren
        headers = dict(scope.get("headers") or [])
        header_bytes = self.header_name.encode("latin-1")
        correlation_id = headers.get(header_bytes)

        if correlation_id is None:
            correlation_id = str(uuid.uuid4()).encode("latin-1")

        # in scope setzen, damit FastAPI sie in request.state übernehmen kann
        scope.setdefault("state", {})
        scope["state"]["correlation_id"] = correlation_id.decode("latin-1")

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                raw_headers = dict(message.get("headers") or [])
                raw_headers[header_bytes] = correlation_id
                message["headers"] = list(raw_headers.items())
            await send(message)

        await self.app(scope, receive, send_wrapper)
