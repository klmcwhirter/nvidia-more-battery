
import logging


def config_logger(*, verbose=False, **kwargs) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='{asctime} - {module} - {funcName} - {levelname} - {message}', style='{')
