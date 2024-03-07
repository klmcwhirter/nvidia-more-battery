'''nvidia_more_battery - Get battery time back by making usage of nvidia GPU optional for systems with Optimus

Usage:
    nvidia_more_battery {disable | enable | has_nvidia} [--help] [--verbose] [--version]

Commands:
    disable         Revert changes made to enable nvidia_more_battery
    enable          Enable changes to use nvidia with more battery time; only works if at least one NVIDIA device is present on the PCI bus
    has_nvidia      Reports whether or not at least one NVIDIA device is present on the PCI bus

Options:
    --verbose       Enable debug logging
    --version       Output the current version and exit
    --help          Show this help

**NOTE** In order to make changes to the system the process must have an effective uid of root (e.g., via sudo).

'''

import logging
import sys
from pprint import pformat
from typing import Any

from nvidia_more_battery.services.tmpfiles import (delete_no_nvidia,
                                                   system_has_nvidia,
                                                   write_no_nvidia)
from nvidia_more_battery.utils.args import args_to_opts
from nvidia_more_battery.utils.logging import config_logger

VERSION = '0.1.0'  # TODO retrieve from pyproject.toml


def main(**kwargs: dict[str, Any]) -> None:
    if 'help' in kwargs and kwargs['help']:
        print(__doc__)
        return
    elif 'version' in kwargs and kwargs['version']:
        print(f'nvidia_more_battery {VERSION}')
        return

    logging.debug(f'starting')

    if 'disable' in kwargs and kwargs['disable']:
        delete_no_nvidia()
    elif 'enable' in kwargs and kwargs['enable']:
        write_no_nvidia()
    elif 'has_nvidia' in kwargs and kwargs['has_nvidia']:
        has_nvidia = 'nvidia' if system_has_nvidia() else 'no-nvidia'
        logging.info(f'{has_nvidia=}')
    else:
        print(__doc__)

    logging.debug(f'done')


if __name__ == '__main__':
    opts = args_to_opts(sys.argv[1:])

    config_logger(**opts)
    logging.debug(pformat(opts, sort_dicts=False))

    main(**opts)
