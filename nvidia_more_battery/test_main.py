

from _pytest.monkeypatch import MonkeyPatch

from nvidia_more_battery.__main__ import main
from nvidia_more_battery.services import tmpfiles
from nvidia_more_battery.utils import pci
from nvidia_more_battery.utils.args import args_to_opts

funcs_called = {}


def capture_function_call(name: str):
    funcs_called[name] = False

    def wrapper() -> None:
        funcs_called[name] = True
        print(f'{name} was called')

    wrapper.__name__ = name

    return wrapper


def test_disable_wo_rescan_does_not_call(monkeypatch: MonkeyPatch):
    global funcs_called
    funcs_called.clear()

    opts = args_to_opts(['disable'])
    print(f'\n{opts=}')

    monkeypatch.setattr(tmpfiles, 'delete_no_nvidia', capture_function_call(tmpfiles.delete_no_nvidia.__name__))
    monkeypatch.setattr(pci, 'rescan_pcie_bus', capture_function_call(pci.rescan_pcie_bus.__name__))

    main(opts)

    assert funcs_called[tmpfiles.delete_no_nvidia.__name__]
    assert not funcs_called[pci.rescan_pcie_bus.__name__], 'should not have called rescan_pcie_bus'


def test_disable_w_rescan_does_call(monkeypatch: MonkeyPatch):
    global funcs_called
    funcs_called.clear()

    opts = args_to_opts(['disable', 'rescan'])
    print(f'\n{opts=}')

    monkeypatch.setattr(tmpfiles, 'delete_no_nvidia', capture_function_call(tmpfiles.delete_no_nvidia.__name__))
    monkeypatch.setattr(pci, 'rescan_pcie_bus', capture_function_call(pci.rescan_pcie_bus.__name__))

    main(opts)

    assert funcs_called[tmpfiles.delete_no_nvidia.__name__]
    assert funcs_called[pci.rescan_pcie_bus.__name__], 'should have called rescan_pcie_bus'
