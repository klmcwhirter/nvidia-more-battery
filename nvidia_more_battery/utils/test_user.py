
import os
import pwd

import pytest

from nvidia_more_battery.utils.user import is_root, uid_gid


class FakePasswd:
    def __init__(self, uid: int, gid: int) -> None:
        self._pw_uid = uid
        self._pw_gid = gid

    @property
    def pw_uid(self) -> int:
        return self._pw_uid

    @property
    def pw_gid(self) -> int:
        return self._pw_gid


def fake_environ(username: str):
    return {**os.environ, 'USERNAME': username}


def fake_geteuid(euid: int):
    def wrapper():
        return euid
    return wrapper


def fake_getpwnam(uid: int, gid: int):
    def wrapper(username: str):
        if username == 'root':
            return FakePasswd(0, 0)

        return FakePasswd(uid, gid)
    return wrapper


@pytest.mark.parametrize(
    'uid,gid,euid,expected',
    [
        (1000, 1000, 1000, False),
        (1000, 1000, 0, True),  # if sudo was used
        (0, 0, 0, True),
    ]
)
def test_is_root(uid: int, gid: int, euid: int, expected: bool, monkeypatch) -> None:
    monkeypatch.setattr(pwd, 'getpwnam', fake_getpwnam(uid, gid))
    monkeypatch.setattr(os, 'geteuid', fake_geteuid(euid))
    rc = is_root()

    assert expected == rc


@pytest.mark.parametrize(
    'username,uid,gid',
    [
        ('someone', 1000, 1000),
        ('root', 0, 0),
    ]
)
def test_uid_gid(username: str, uid: int, gid: int, monkeypatch) -> None:
    monkeypatch.setattr(pwd, 'getpwnam', fake_getpwnam(uid, gid))
    monkeypatch.setattr(os, 'environ', fake_environ(username))
    rc_uid, rc_gid = uid_gid()

    assert uid == rc_uid
    assert gid == rc_gid
