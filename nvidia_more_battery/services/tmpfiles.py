
import logging
import os
import shutil

from nvidia_more_battery.utils import pci, user

NO_NVIDIA_TMPFILE = '/etc/tmpfiles.d/nvidia_no_gpu.conf'

RUN_NO_NVIDIA_IN_EFFECT = '/run/no-nvidia/in-effect'
RUN_NO_NVIDIA = os.path.dirname(RUN_NO_NVIDIA_IN_EFFECT)


def delete_no_nvidia() -> None:
    if os.path.exists(NO_NVIDIA_TMPFILE):
        user.assure_root()

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


def write_no_nvidia() -> None:
    logging.debug(f'{RUN_NO_NVIDIA_IN_EFFECT=}')

    nvidia_ids = pci.find_nvidia_ids_from_lspci()

    is_root = user.is_root()
    pci.assure_hybrid_and_root(nvidia_ids, is_root)

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
        for dir in pci.find_nvidia_sys_device_dirs(id):
            tmpfiles_content.append(f'w {dir}/remove - - - - 1\n')

    tmpfiles_content.append('\n')

    # Log the content before the is_root assertion
    logging.debug('tmpfiles_content=')
    for s in tmpfiles_content:
        print(s, end='')

    user.assure_root()

    with open(NO_NVIDIA_TMPFILE, 'w') as f:
        f.writelines(tmpfiles_content)

    logging.debug(f'Created {NO_NVIDIA_TMPFILE}')
