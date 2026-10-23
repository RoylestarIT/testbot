import sys

from loguru import logger

from app.core.config import Settings


def setup_logging(settings: Settings) -> None:
    if settings.sentry_dsn.strip():
        try:
            import sentry_sdk

            sentry_sdk.init(dsn=settings.sentry_dsn.strip(), traces_sample_rate=0.1)
        except Exception:
            logger.warning("Sentry init failed")

    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.log_level.upper(),
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
    )
