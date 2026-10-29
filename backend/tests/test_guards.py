from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.body_limit import BodyLimit
from app.clientip import client_ip
from app.ratelimit import SlidingWindowLimiter


def echo_app(trust_proxy: bool) -> TestClient:
    app = FastAPI()
    app.add_middleware(BodyLimit, limit=32)

    @app.post("/echo")
    async def echo(request: Request) -> dict:
        await request.body()
        return {"ip": client_ip(request, trust_proxy)}

    return TestClient(app)


def test_prefers_the_address_cloudflare_saw_over_a_forged_forwarded_header():
    headers = {"cf-connecting-ip": "203.0.113.7", "x-forwarded-for": "198.51.100.1, 203.0.113.7"}
    assert echo_app(True).post("/echo", headers=headers).json() == {"ip": "203.0.113.7"}


def test_ignores_proxy_headers_unless_the_proxy_is_trusted():
    headers = {"cf-connecting-ip": "203.0.113.7", "x-forwarded-for": "198.51.100.1"}
    assert echo_app(False).post("/echo", headers=headers).json() == {"ip": "testclient"}


def test_refuses_bodies_larger_than_the_limit():
    client = echo_app(False)
    assert client.post("/echo", content=b"x" * 16).status_code == 200
    assert client.post("/echo", content=b"x" * 64).status_code == 413
    assert client.post("/echo", content=iter([b"x" * 20, b"x" * 20])).status_code == 413


def test_forgets_clients_once_their_window_passes():
    limiter = SlidingWindowLimiter(1, 60)
    for index in range(100):
        limiter.allow(f"203.0.113.{index}", now=0)
    limiter.allow("198.51.100.1", now=120)
    assert limiter.tracked == 1
