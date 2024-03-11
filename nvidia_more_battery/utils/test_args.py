

import pytest

from nvidia_more_battery.utils.args import (args_to_opts, opt_is_enabled,
                                            strip_dashes)


def test_args_to_opts_does_not_throw() -> None:
    rc = args_to_opts([])
    assert rc is not None


@pytest.mark.parametrize(
    'args_list,expected',
    [
        (['--stdout', 'nodash', '--verbose'], {'stdout': True, 'nodash': True, 'verbose': True}),
        (['--stdout', 'no-dash-', '-v'], {'stdout': True, 'no-dash-': True, 'v': True})
    ]
)
def test_args_to_opts_strips_dashes(args_list: list[str], expected: dict[str, bool]) -> None:
    rc = args_to_opts(args_list)
    assert expected == rc


@pytest.fixture
def opts_for_test() -> dict[str, bool]:
    return {
        'stdout': True,
        'verbose': True
    }


@pytest.mark.parametrize(
    'opt,expected',
    [
        ('verbose', True),
        ('bogus', False)
    ]
)
def test_opt_is_enabled(opts_for_test: dict[str, bool], opt: str, expected: bool) -> None:
    rc = opt_is_enabled(opt, opts_for_test)
    assert expected == rc


@pytest.mark.parametrize(
    'opt,expected',
    [
        ('-h', 'h'),
        ('nothing_here', 'nothing_here'),
        # Only strips from the left
        ('no-dash-', 'no-dash-')
    ]
)
def test_strip_dashes_does_it(opt: str, expected: str) -> None:
    rc = strip_dashes(opt)
    assert expected == rc
