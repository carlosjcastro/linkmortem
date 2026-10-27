import logging

import sentry_sdk

from app.config import Settings


IP_TERMS = ["forwarded", "-ip", "remote-", "via", "-user"]
PRIVATE_DATA_COLLECTION = {
    "user_info": False,
    "cookies": {"mode": "off"},
    "http_bodies": [],
    "http_headers": {"request": {"mode": "denylist", "terms": IP_TERMS}},
    "url_query_params": {"mode": "denylist", "terms": IP_TERMS},
    "gen_ai": {"inputs": False, "outputs": False},
    "database_query_data": False,
}
LOG_FORMAT = "%(levelname)s:     %(name)s %(message)s"


def configure_logging() -> None:
    logger = logging.getLogger("linkmortem")
    if logger.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def init_telemetry(settings: Settings) -> bool:
    if not settings.sentry_dsn:
        return False
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=1.0,
        data_collection=PRIVATE_DATA_COLLECTION,
    )
    return True
