'''nvidia_more_battery - Get battery time back by making usage of nvidia GPU optional for systems with Optimus

Usage:
    nvidia_mode_battery enable [--verbose]
    nvidia_mode_battery has_nvidia [--verbose]
    nvidia_mode_battery disable [--verbose]

Verbs:
    enable          Enable changes to use nvidia with more battery time; only works if at least one NVIDIA device is present on the PCI bus
    has_nvidia      Reports whether or not at least one NVIDIA device is present on the PCI bus
    disable         Revert changes made to enable nvidia_more_battery

Options:
    -v, --verbose   Enable debug logging
    --version       Output the current version and exit


**NOTE** In order to make changes to the system the process must have an effective uid of root (e.g., via sudo).

'''
import logging
from pprint import pformat
from typing import Any

from nvidia_more_battery.logging import config_logger
from nvidia_more_battery.tmpfiles import (delete_no_nvidia, system_has_nvidia,
                                          write_no_nvidia)


def cmd_disable(**kwargs: dict[str, Any]) -> None:
    logging.debug('starting')
    delete_no_nvidia()
    logging.debug('done')


def cmd_enable(**kwargs: dict[str, Any]) -> None:
    logging.debug('starting')
    write_no_nvidia()
    logging.debug('done')


def cmd_has_nvidia(**kwargs: dict[str, Any]) -> None:
    logging.debug('starting')
    has_nvidia = 'nvidia' if system_has_nvidia() else 'no-nvidia'
    logging.info(f'{has_nvidia=}')
    logging.debug('done')


def main(**kwargs: dict[str, Any]) -> None:
    cmds = {
        'disable': cmd_disable,
        'enable': cmd_enable,
        'has_nvidia': cmd_has_nvidia,
    }

    cmd = [cmd for k, cmd in cmds.items() if k in kwargs and kwargs[k]][0]
    cmd(**kwargs)


VERSION = '0.1.0'  # TODO retrieve from pyproject.toml


if __name__ == '__main__':
    from docopt import docopt
    opts = docopt(__doc__, version=VERSION)
    config_logger(**opts)
    logging.debug(pformat(opts, sort_dicts=False))

    main(**opts)
