"""Filtering functions."""

from speculum.config import Configuration


__all__ = ['match']


def match_country(config: Configuration, mirror: dict) -> bool:
    """Matches country names an codes."""

    if config.countries is None:
        return True

    if country := mirror.get('country'):
        if country.casefold() in config.countries:
            return True

    if country_code := mirror.get('country_code'):
        if country_code.casefold() in config.countries:
            return True

    return False


def match_protocols(config: Configuration, mirror: dict) -> bool:
    """Matches protocol restrictions."""

    if config.protocols is None:
        return True

    if protocol := mirror.get('protocol'):
        return protocol.casefold() in config.protocols

    return False


def match_max_age(config: Configuration, mirror: dict) -> bool:
    """Matches maximum age restrictions."""

    if config.max_age is None:
        return True

    if age := mirror.get('age') is not None:
        return age <= config.max_age

    return False


def match_regex(config: Configuration, mirror: dict) -> bool:
    """Matches regular expressions."""

    if config.match is None:
        return True

    if url := mirror.get('url'):
        return config.match.search(url)

    return False


def match_regex_inv(config: Configuration, mirror: dict) -> bool:
    """Negative matches regular expressions."""

    if config.nomatch is None:
        return True

    if url := mirror.get('url'):
        return config.nomatch.search(url)

    return False


def match_complete(config: Configuration, mirror: dict) -> bool:
    """Matches complete mirrors."""

    if not config.complete:
        return True

    return mirror.get('completion_pct') == 1


def match_active(config: Configuration, mirror: dict) -> bool:
    """Matches active mirrors."""

    if not config.active:
        return True

    return mirror.get('active')


def match_ipv4(config: Configuration, mirror: dict) -> bool:
    """Matches IPv4 enabled mirrors."""

    if not config.ipv4:
        return True

    return mirror.get('ipv4')


def match_ipv6(config: Configuration, mirror: dict) -> bool:
    """Matches IPv6 enabled mirrors."""

    if not config.ipv6:
        return True

    return mirror.get('ipv6')


def match_isos(config: Configuration, mirror: dict) -> bool:
    """Matches mirrors that host ISOs."""

    if not config.isos:
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


def match(config: Configuration, mirror: dict) -> bool:
    """Filters the respective mirrors."""

    return all(match_func(config, mirror) for match_func in MATCH_FUNCS)
