
import logging

import pytest

from nvidia_more_battery.utils.logging import config_logger


@pytest.mark.parametrize(
    'verbose',
    [
        (False),
        (True),
    ]
)
def test_config_logger(caplog: pytest.LogCaptureFixture, verbose: bool) -> None:
    config_logger(verbose=verbose)

    print(f'{logging.getLogger().level=}')

    logging.debug('debug')
    logging.info('info')

    # print(caplog.record_tuples)

    if verbose:
        assert any(level == logging.DEBUG for _, level, _ in caplog.record_tuples)
    else:
        assert all(level != logging.DEBUG for _, level, _ in caplog.record_tuples)
