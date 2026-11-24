import re
import uuid

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class CorrelationIdMiddleware:
    def __init__(self, app: ASGIApp, header_name: str = "X-Correlation-ID") -> None:
        self.app = app
        self.header_name = header_name.lower().encode("ascii")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        candidates = [value for name, value in scope.get("headers", [])
                      if name.lower() == self.header_name]
        # Never echo arbitrary client bytes into response headers or logs.
        if len(candidates) == 1 and re.fullmatch(rb"[A-Za-z0-9._:-]{1,128}", candidates[0]):
            correlation_id = candidates[0]
        else:
            correlation_id = str(uuid.uuid4()).encode("ascii")
        scope.setdefault("state", {})["correlation_id"] = correlation_id.decode("ascii")

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                # Preserve repeated headers such as Set-Cookie.
                headers = [(name, value) for name, value in message.get("headers", [])
                           if name.lower() != self.header_name]
                message = {**message, "headers": [*headers, (self.header_name, correlation_id)]}
            await send(message)

        await self.app(scope, receive, send_wrapper)
