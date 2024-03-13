
import logging


def config_logger(*, verbose: bool = False, **_kwargs) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='{asctime} - {module} - {funcName} - {levelname} - {message}', style='{')
    logging.getLogger().setLevel(level=level)
