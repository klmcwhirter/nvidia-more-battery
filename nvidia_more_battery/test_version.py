

def test_version_can_import() -> None:
    from ._version import __version__
    assert __version__ is not None
