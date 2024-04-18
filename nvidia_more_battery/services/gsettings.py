
import logging

# Needed to enable touchpad gestures with Wayland
WAYLAND_GESTURES = 'gsettings set org.gnome.mutter experimental-features [\"kms-modifiers\"]'
RESET_WAYLAND_GESTURES = 'gsettings reset org.gnome.mutter experimental-features'


def _announce(msg: str) -> None:
    logging.info(f'''
Execute the following as your non-root user:

{msg}
          ''')


def set_touchpad_support() -> None:
    _announce(WAYLAND_GESTURES)


def reset_touchpad_support() -> None:
    _announce(RESET_WAYLAND_GESTURES)
