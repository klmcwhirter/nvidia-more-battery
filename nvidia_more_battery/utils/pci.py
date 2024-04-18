

import logging
import subprocess

from nvidia_more_battery.utils.user import MUST_BE_ROOT

MUST_BE_HYBRID = 'System must be in hybrid Optimus mode'

PCI_BUS_RESCAN = '/sys/bus/pci/rescan'


def assure_hybrid_and_root(nvidia_ids: set[str] | None = None, is_root: bool = False) -> None:
    if not nvidia_ids:
        nvidia_ids = find_nvidia_ids_from_lspci()

    if len(nvidia_ids) < 1:
        msg = MUST_BE_HYBRID if is_root else f'{MUST_BE_HYBRID} and {MUST_BE_ROOT}'
        raise SystemError(msg)


def find_nvidia_sys_device_dirs(nvidia_lspci_id) -> list[str]:
    output = subprocess.check_output(['find', '/sys/devices', '-type', 'd', '-name', f'{nvidia_lspci_id}.*']).decode('utf-8')
    dirs = [dir for dir in output.splitlines() if 'virtual' not in dir]
    return dirs


def find_nvidia_ids_from_lspci() -> set[str]:
    lspci_output = subprocess.check_output(['lspci']).decode('utf-8')
    ids = {line.split('.')[0]
           for line in lspci_output.splitlines()
           if 'NVIDIA' in line}
    return ids


def rescan_pcie_bus() -> None:
    logging.debug(f'Writing 1 to {PCI_BUS_RESCAN} ...')

    with open(PCI_BUS_RESCAN, 'w') as f:
        f.write('1')

    logging.debug(f'Writing 1 to {PCI_BUS_RESCAN} ... done')


def system_has_nvidia() -> bool:
    return len(find_nvidia_ids_from_lspci()) >= 1
