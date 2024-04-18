
import subprocess
from typing import Callable

import pytest

from nvidia_more_battery.utils import pci


def fake_ids() -> set[str]:
    return {
        '0000:01:00',
    }


@pytest.mark.parametrize(
    'ids,expected',
    [
        # No ids to return from find_nvidia_ids_from_lspci, should return False
        (lambda: set([]), False),
        (fake_ids, True)
    ]
)
def test_system_has_nvidia(monkeypatch, ids: Callable[[], set[str]], expected: bool):
    monkeypatch.setattr(pci, "find_nvidia_ids_from_lspci", ids)

    rc = pci.system_has_nvidia()
    assert expected == rc


def test_find_nvidia_ids_from_lspci_should_return_nvidia(monkeypatch):
    def mockreturn(*_args, **_kwargs) -> bytes:
        return '''
0000:00:02.0  Intel
0000:01:00.0 VGA compatible controller: NVIDIA Corporation GA107M [GeForce RTX 3050 Ti Mobile] (rev a1)
0000:01:00.1 Audio device: NVIDIA Corporation Device 2291 (rev a1)
        '''.encode()

    monkeypatch.setattr(subprocess, "check_output", mockreturn)

    ids = pci.find_nvidia_ids_from_lspci()

    expected = fake_ids()
    assert expected == ids
