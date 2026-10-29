from fastapi import Request

EDGE_HEADER = "cf-connecting-ip"


def client_ip(request: Request, trust_proxy: bool) -> str:
    if trust_proxy:
        edge = request.headers.get(EDGE_HEADER, "").strip()
        if edge:
            return edge
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
