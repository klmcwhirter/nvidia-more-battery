'''nvidia_more_battery - Get battery time back by making usage of nvidia GPU optional for systems with Optimus

Usage:
    nvidia_more_battery {disable | enable | disable-wayland | wayland | has_nvidia} [--rescan] [--help] [--verbose] [--version]

Commands:
    disable         Revert changes made to enable nvidia_more_battery
    enable          Enable changes to use nvidia with more battery time; only works if at least one NVIDIA device is present on the PCI bus
    disable-wayland Revert changes made to enable wayland support
    wayland         Enable wayland settings for hybrid mode; touchpad gestures workaround, etc.
    has_nvidia      Reports whether or not at least one NVIDIA device is present on the PCI bus

Options:
    --rescan        Optionally rescan PCI bus when disable is executed
    --verbose       Enable debug logging
    --version       Output the current version and exit
    --help          Show this help

**NOTE** In order to make changes to the system the process must have an effective uid of root (e.g., via sudo).

'''

import logging
import sys
from pprint import pformat

from nvidia_more_battery._version import __version__
from nvidia_more_battery.services import gsettings, modprobe, tmpfiles
from nvidia_more_battery.utils import pci
from nvidia_more_battery.utils.args import args_to_opts, opt_is_enabled
from nvidia_more_battery.utils.logging import config_logger


def main(opts: dict[str, bool]) -> None:
    if opt_is_enabled('help', opts):
        print(__doc__)
        return
    elif opt_is_enabled('version', opts):
        print(f'nvidia_more_battery {__version__}')
        return

    logging.debug('starting')

    if opt_is_enabled('disable', opts):
        tmpfiles.delete_no_nvidia()

        if opt_is_enabled('rescan', opts):
            pci.rescan_pcie_bus()
        else:
            logging.info('Please reboot so changes can take effect.')
    elif opt_is_enabled('enable', opts):
        tmpfiles.write_no_nvidia()
        logging.info('Please reboot so changes can take effect.')
    elif opt_is_enabled('disable-wayland', opts):
        modprobe.delete_nvidia_wayland()
        gsettings.reset_touchpad_support()
        logging.info('Please reboot so changes can take effect.')
    elif opt_is_enabled('wayland', opts):
        modprobe.write_nvidia_wayland()
        gsettings.set_touchpad_support()
        logging.info('Please reboot so changes can take effect.')
    elif opt_is_enabled('has_nvidia', opts):
        has_nvidia = 'nvidia' if pci.system_has_nvidia() else 'no-nvidia'
        logging.info(f'{has_nvidia=}')
    else:
        print(__doc__)

    logging.debug('done')


if __name__ == '__main__':
    opts = args_to_opts(sys.argv[1:])

    config_logger(**opts)
    logging.debug(pformat(opts, sort_dicts=False))

    main(opts)
