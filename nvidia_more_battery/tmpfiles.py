
import logging
import os
import subprocess

from nvidia_more_battery.user import is_root, uid_gid

NO_NVIDIA_TMPFILE = '/etc/tmpfiles.d/nvidia_no_gpu.conf'
RUN_NO_NVIDIA = f'/run/no-nvidia'
RUN_NO_NVIDIA_IN_EFFECT = os.path.join(RUN_NO_NVIDIA, 'in-effect')


def delete_no_nvidia():
    if os.path.exists(NO_NVIDIA_TMPFILE):
        assert is_root(), 'Must be root to perform operation'

        os.remove(NO_NVIDIA_TMPFILE)

        logging.debug(f'Removed {NO_NVIDIA_TMPFILE}')
    else:
        logging.warn(f'File {NO_NVIDIA_TMPFILE} does not exist - skipping removal.')


def system_has_nvidia():
    return len(find_nvidia_ids_from_lspci()) >= 1


def write_no_nvidia():
    logging.debug(f'{RUN_NO_NVIDIA_IN_EFFECT=}')

    nvidia_ids = find_nvidia_ids_from_lspci()
    if len(nvidia_ids) < 1:
        raise SystemError('System must be in hybrid Optimus mode')

    # 'd /run/no-nvidia 0755 klmcw klmcw\n',
    # 'f /run/no-nvidia/in-effect 0644 klmcw klmcw - 1\n'
    uid, gid = uid_gid()
    tmpfile_content = [
        f'd {RUN_NO_NVIDIA} 0755 {uid} {gid}\n',
        f'f {RUN_NO_NVIDIA_IN_EFFECT} 0444 {uid} {gid} - 1\n'
    ]

    # see find /sys/devices -type d -name '0000:01:00.*'
    # 'w /sys/devices/pci0000:00/0000:00:01.0/0000:01:00.0/remove - - - - 1\n',
    # 'w /sys/devices/pci0000:00/0000:00:01.0/0000:01:00.1/remove - - - - 1\n',
    for id in nvidia_ids:
        # logging.debug(f'Processing nvidia id={id}')
        for dir in find_nvidia_sys_device_dirs(id):
            tmpfile_content.append(f'w {dir}/remove - - - - 1\n')

    tmpfile_content.append('\n')

    assert is_root(), 'Must be root to perform operation'

    with open(NO_NVIDIA_TMPFILE, 'w') as f:
        f.writelines(tmpfile_content)

    logging.debug(f'Created {NO_NVIDIA_TMPFILE}')


def find_nvidia_sys_device_dirs(nvidia_lspci_id):
    output = subprocess.check_output(['find', '/sys/devices', '-type', 'd', '-name', f'{nvidia_lspci_id}.*']).decode('utf-8')
    dirs = [dir for dir in output.splitlines() if 'virtual' not in dir]
    return dirs


def find_nvidia_ids_from_lspci():
    lspci_output = subprocess.check_output(['lspci']).decode('utf-8')
    ids = {line.split('.')[0]
           for line in lspci_output.splitlines()
           if 'NVIDIA' in line}
    return ids
