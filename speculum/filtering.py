"""Filtering functions."""

from argparse import Namespace


__all__ = ['match']


def match_country(args: Namespace, mirror: dict) -> bool:
    """Matches country names an codes."""

    if args.countries is None:
        return True

    if country := mirror.get('country'):
        if country.casefold() in args.countries:
            return True

    if country_code := mirror.get('country_code'):
        if country_code.casefold() in args.countries:
            return True

    return False


def match_protocols(args: Namespace, mirror: dict) -> bool:
    """Matches protocol restrictions."""

    if args.protocols is None:
        return True

    if protocol := mirror.get('protocol'):
        return protocol.casefold() in args.protocols

    return False


def match_max_age(args: Namespace, mirror: dict) -> bool:
    """Matches maximum age restrictions."""

    if args.max_age is None:
        return True

    if age := mirror.get('age') is not None:
        return age <= args.max_age

    return False


def match_regex(args: Namespace, mirror: dict) -> bool:
    """Matches regular expressions."""

    if args.match is None:
        return True

    if url := mirror.get('url'):
        return args.match.match(url)

    return False


def match_regex_inv(args: Namespace, mirror: dict) -> bool:
    """Negative matches regular expressions."""

    if args.nomatch is None:
        return True

    if url := mirror.get('url'):
        return args.nomatch.match(url)

    return False


def match_complete(args: Namespace, mirror: dict) -> bool:
    """Matches complete mirrors."""

    if not args.complete:
        return True

    return mirror.get('completion_pct') == 1


def match_active(args: Namespace, mirror: dict) -> bool:
    """Matches active mirrors."""

    if not args.active:
        return True

    return mirror.get('active')


def match_ipv4(args: Namespace, mirror: dict) -> bool:
    """Matches IPv4 enabled mirrors."""

    if not args.ipv4:
        return True

    return mirror.get('ipv4')


def match_ipv6(args: Namespace, mirror: dict) -> bool:
    """Matches IPv6 enabled mirrors."""

    if not args.ipv6:
        return True

    return mirror.get('ipv6')


def match_isos(args: Namespace, mirror: dict) -> bool:
    """Matches mirrors that host ISOs."""

    if not args.isos:
        return True

    return mirror.get('isos')


MATCH_FUNCS = (
    match_country,
    match_protocols,
    match_max_age,
    match_regex,
    match_regex_inv,
    match_complete,
    match_active,
    match_ipv4,
    match_ipv6,
    match_isos
)


def match(args: Namespace, mirror: dict) -> bool:
    """Filters the respective mirrors."""

    return all(match_func(args, mirror) for match_func in MATCH_FUNCS)
