
import logging
import os

from nvidia_more_battery.utils import pci, user

WAYLAND_FILE = '/etc/modprobe.d/nvidia_more_battery-wayland.conf'

WAYLAND_CONTENT = '''
# Automatically generated by nvidia_more_battery

# Needed to enable touchpad gestures with Wayland
options nvidia-drm modeset=1
options nvidia NVreg_UsePageAttributeTable=1 NVreg_InitializeSystemMemoryAllocations=0

'''


def delete_nvidia_wayland() -> None:
    logging.debug(f'{WAYLAND_FILE=}')

    if os.path.exists(WAYLAND_FILE):
        user.assure_root()

        os.remove(WAYLAND_FILE)

        logging.debug(f'Removed {WAYLAND_FILE}')
    else:
        logging.warn(f'File {WAYLAND_FILE} does not exist - skipping removal.')


def write_nvidia_wayland() -> None:
    logging.debug(f'{WAYLAND_FILE=}')

    pci.assure_hybrid_and_root(is_root=user.is_root())

    user.assure_root()

    with open(WAYLAND_FILE, 'w') as f:
        f.writelines(WAYLAND_CONTENT)

    logging.debug(f'Created {WAYLAND_FILE}')
