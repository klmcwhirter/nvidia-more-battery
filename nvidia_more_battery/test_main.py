

from _pytest.monkeypatch import MonkeyPatch

import nvidia_more_battery.services.tmpfiles
from nvidia_more_battery.__main__ import (delete_no_nvidia, main,
                                          rescan_pcie_bus)
from nvidia_more_battery.utils.args import args_to_opts

funcs_called = {}


def capture_function_call(name: str):
    funcs_called[name] = False

    def wrapper() -> None:
        funcs_called[name] = True
        print(f'{name} was called')

    return wrapper


def test_disable_wo_rescan_does_not_call(monkeypatch: MonkeyPatch):
    global funcs_called
    funcs_called.clear()

    opts = args_to_opts(['disable'])
    print(f'\n{opts=}')

    monkeypatch.setattr(nvidia_more_battery.__main__, 'delete_no_nvidia', capture_function_call(delete_no_nvidia.__name__))
    monkeypatch.setattr(nvidia_more_battery.__main__, 'rescan_pcie_bus', capture_function_call(rescan_pcie_bus.__name__))

    main(opts)

    assert funcs_called[delete_no_nvidia.__name__]
    assert not funcs_called[rescan_pcie_bus.__name__], 'should not have called rescan_pcie_bus'


def test_disable_w_rescan_does_call(monkeypatch: MonkeyPatch):
    global funcs_called
    funcs_called.clear()

    opts = args_to_opts(['disable', 'rescan'])
    print(f'\n{opts=}')

    monkeypatch.setattr(nvidia_more_battery.__main__, 'delete_no_nvidia', capture_function_call(delete_no_nvidia.__name__))
    monkeypatch.setattr(nvidia_more_battery.__main__, 'rescan_pcie_bus', capture_function_call(rescan_pcie_bus.__name__))

    main(opts)

    assert funcs_called[delete_no_nvidia.__name__]
    assert funcs_called[rescan_pcie_bus.__name__], 'should have called rescan_pcie_bus'
