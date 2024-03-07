
def args_to_opts(args: list[str]) -> dict[str, bool]:
    return {
        strip_dashes(arg): True
        for arg in args
    }


def strip_dashes(s: str) -> None:
    return s.lstrip('-')
