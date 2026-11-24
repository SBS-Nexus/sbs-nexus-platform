import asyncio
import uuid

import pytest

from shared.infra.correlation_id_middleware import CorrelationIdMiddleware


def invoke(headers, kind="http"):
    scope = {"type": kind, "headers": headers}
    sent = []

    async def app(scope, receive, send):
        await send({"type": "http.response.start", "status": 200, "headers": [
            (b"set-cookie", b"a=1"), (b"set-cookie", b"b=2"),
            (b"X-Correlation-ID", b"old"),
        ]})

    async def receive():
        return {"type": "http.request", "body": b""}

    async def send(message):
        sent.append(message)

    asyncio.run(CorrelationIdMiddleware(app)(scope, receive, send))
    return scope, sent[0]


def test_client_identifier_and_repeated_response_headers_survive():
    scope, response = invoke([(b"x-correlation-id", b"request-123")])
    assert scope["state"]["correlation_id"] == "request-123"
    assert response["headers"] == [
        (b"set-cookie", b"a=1"), (b"set-cookie", b"b=2"),
        (b"x-correlation-id", b"request-123"),
    ]


@pytest.mark.parametrize("headers", [
    [], [(b"x-correlation-id", b"")], [(b"x-correlation-id", b"x" * 129)],
    [(b"x-correlation-id", b"unsafe\r\nvalue")],
    [(b"x-correlation-id", b"first"), (b"x-correlation-id", b"second")],
])
def test_missing_or_invalid_identifier_is_replaced(headers):
    scope, response = invoke(headers)
    value = scope["state"]["correlation_id"]
    assert str(uuid.UUID(value)) == value
    assert (b"x-correlation-id", value.encode("ascii")) in response["headers"]


def test_non_http_scope_is_passed_through():
    scope, response = invoke([], kind="websocket")
    assert "state" not in scope
    assert (b"X-Correlation-ID", b"old") in response["headers"]
