'''minimal args parsing utilities'''


def args_to_opts(args: list[str]) -> dict[str, bool]:
    return {
        strip_dashes(arg): True
        for arg in args
    }


def opt_is_enabled(opt: str, opts: dict[str, bool]) -> bool:
    return bool(opt in opts and opts[opt])


def strip_dashes(s: str) -> str:
    return s.lstrip('-')
