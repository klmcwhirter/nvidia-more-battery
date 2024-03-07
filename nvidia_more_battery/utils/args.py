'''minimal args parsing utilities'''


def args_to_opts(args: list[str]) -> dict[str, bool]:
    return {
        strip_dashes(arg): True
        for arg in args
    }


def opt_is_enabled(opt: str, **kwargs: dict[str, bool]) -> bool:
    return opt in kwargs and kwargs[opt]


def strip_dashes(s: str) -> None:
    return s.lstrip('-')
