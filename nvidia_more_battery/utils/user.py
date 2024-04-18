
import logging
import os
import pwd

MUST_BE_ROOT = 'User must have root permissions to perform operation'


def assure_root() -> None:
    if not is_root():
        raise SystemError(MUST_BE_ROOT)


def is_root() -> bool:
    root = pwd.getpwnam('root')
    logging.debug(f'{os.geteuid()=}, {root.pw_uid=}')
    return os.geteuid() == root.pw_uid


def uid_gid() -> tuple[int, int]:
    # USERNAME survives simple no-login sudo
    username = os.environ['USERNAME'] if 'USERNAME' in os.environ else 'root'
    logging.debug(f'username={username}')
    user = pwd.getpwnam(username)
    logging.debug(f'user={user}')
    return (user.pw_uid, user.pw_gid)
