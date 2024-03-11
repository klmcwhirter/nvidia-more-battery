
import logging
import os
import shutil
import subprocess

from nvidia_more_battery.utils import user

MUST_BE_HYBRID = 'System must be in hybrid Optimus mode'
MUST_BE_ROOT = 'User must have root permissions to perform operation'

NO_NVIDIA_TMPFILE = '/etc/tmpfiles.d/nvidia_no_gpu.conf'

PCI_BUS_RESCAN = '/sys/bus/pci/rescan'

RUN_NO_NVIDIA_IN_EFFECT = '/run/no-nvidia/in-effect'
RUN_NO_NVIDIA = os.path.dirname(RUN_NO_NVIDIA_IN_EFFECT)


def delete_no_nvidia() -> None:
    if os.path.exists(NO_NVIDIA_TMPFILE):
        assert user.is_root(), MUST_BE_ROOT

        os.remove(NO_NVIDIA_TMPFILE)
        logging.debug(f'Removed {NO_NVIDIA_TMPFILE}')
    else:
        logging.warn(f'File {NO_NVIDIA_TMPFILE} does not exist - skipping removal.')

    if os.path.exists(RUN_NO_NVIDIA_IN_EFFECT):
        os.remove(RUN_NO_NVIDIA_IN_EFFECT)
        logging.debug(f'Removed {RUN_NO_NVIDIA_IN_EFFECT}')

        shutil.rmtree(RUN_NO_NVIDIA)
        logging.debug(f'Removed {RUN_NO_NVIDIA}')
    else:
        logging.warn(f'File {RUN_NO_NVIDIA_IN_EFFECT} does not exist - skipping removal.')


def rescan_pcie_bus() -> None:
    logging.debug(f'Writing 1 to {PCI_BUS_RESCAN} ...')

    with open(PCI_BUS_RESCAN, 'w') as f:
        f.write('1')

    logging.debug(f'Writing 1 to {PCI_BUS_RESCAN} ... done')


def system_has_nvidia() -> bool:
    return len(find_nvidia_ids_from_lspci()) >= 1


def write_no_nvidia() -> None:
    logging.debug(f'{RUN_NO_NVIDIA_IN_EFFECT=}')
    is_root = user.is_root()

    nvidia_ids = find_nvidia_ids_from_lspci()
    if len(nvidia_ids) < 1:
        msg = MUST_BE_HYBRID if is_root else f'{MUST_BE_HYBRID} and {MUST_BE_ROOT}'
        raise SystemError(msg)

    # 'd /run/no-nvidia 0755 klmcw klmcw\n',
    # 'f /run/no-nvidia/in-effect 0644 klmcw klmcw - 1\n'
    uid, gid = user.uid_gid()
    tmpfiles_content = [
        f'd {RUN_NO_NVIDIA} 0755 {uid} {gid}\n',
        f'f {RUN_NO_NVIDIA_IN_EFFECT} 0444 {uid} {gid} - 1\n'
    ]

    # see find /sys/devices -type d -name '0000:01:00.*'
    # 'w /sys/devices/pci0000:00/0000:00:01.0/0000:01:00.0/remove - - - - 1\n',
    # 'w /sys/devices/pci0000:00/0000:00:01.0/0000:01:00.1/remove - - - - 1\n',
    for id in nvidia_ids:
        # logging.debug(f'Processing nvidia id={id}')
        for dir in find_nvidia_sys_device_dirs(id):
            tmpfiles_content.append(f'w {dir}/remove - - - - 1\n')

    tmpfiles_content.append('\n')

    # Log the content before the is_root assertion
    logging.debug('tmpfiles_content=')
    for s in tmpfiles_content:
        print(s, end='')

    assert user.is_root(), MUST_BE_ROOT

    with open(NO_NVIDIA_TMPFILE, 'w') as f:
        f.writelines(tmpfiles_content)

    logging.debug(f'Created {NO_NVIDIA_TMPFILE}')


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
