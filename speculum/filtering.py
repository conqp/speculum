"""Filtering functions."""

from datetime import datetime, timedelta
from functools import partial
from re import search
from typing import Callable, Iterable, Iterator

from speculum.config import Configuration
from speculum.parsers import parse_datetime


__all__ = ['get_filters', 'match']


def match_country(countries: list[str], mirror: dict) -> bool:
    """Matches country names or codes."""

    if country := mirror.get('country'):
        if country.casefold() in countries:
            return True

    if country_code := mirror.get('country_code'):
        if country_code.casefold() in countries:
            return True

    return False


def match_protocols(protocols: list[str], mirror: dict) -> bool:
    """Matches protocol restrictions."""

    if protocol := mirror.get('protocol'):
        return protocol.casefold() in protocols

    return False


def match_max_age(now: datetime, max_age: timedelta, mirror: dict) -> bool:
    """Matches maximum age restrictions."""

    if last_sync := mirror.get('last_sync'):
        return now - parse_datetime(last_sync) <= max_age

    return False


def match_regex(pattern: str, mirror: dict, *, inverse: bool = False) -> bool:
    """Matches regular expressions."""

    if not (url := mirror.get('url')):
        return False

    if inverse:
        return not search(pattern, url)

    return bool(search(pattern, url))


def get_filters(config: Configuration) -> Iterator[Callable[[dict], bool]]:
    """Yields functions to match the given mirror."""

    if config.countries:
        yield partial(match_country, config.countries)

    if config.protocols:
        yield partial(match_protocols, config.protocols)

    if config.max_age is not None:
        yield partial(match_max_age, datetime.now(), config.max_age)

    if config.match is not None:
        yield partial(match_regex, config.match)

    if config.nomatch is not None:
        yield partial(match_regex, config.nomatch, inverse=True)

    if config.complete:
        yield lambda mirror: mirror.get('completion_pct') == 1

    if config.active:
        yield lambda mirror: mirror.get('active', False)

    if config.ipv4:
        yield lambda mirror: mirror.get('ipv4', False)

    if config.ipv6:
        yield lambda mirror: mirror.get('ipv6', False)

    if config.isos:
        yield lambda mirror: mirror.get('isos', False)


def match(functions: Iterable[Callable[[dict], bool]], mirror: dict) -> bool:
    """Filters the respective mirrors."""

    return all(function(mirror) for function in functions)
