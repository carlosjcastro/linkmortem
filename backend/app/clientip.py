from fastapi import Request


def client_ip(request: Request, trust_proxy: bool) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if trust_proxy and forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
