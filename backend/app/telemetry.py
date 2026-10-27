import logging

import sentry_sdk

from app.config import Settings


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
        send_default_pii=False,
    )
    return True
