"""Mirror handling."""

from datetime import datetime
from json import load
from typing import Iterable, Iterator, NamedTuple, Optional
from urllib.parse import urlparse, urlunparse
from urllib.request import urlopen

from speculum.config import Configuration
from speculum.io import iterprint
from speculum.logging import LOGGER


__all__ = ['SORTING_DEFAULTS', 'get_mirrors', 'get_lines', 'list_countries']


MIRRORS_URL = 'https://www.archlinux.org/mirrors/status/json/'
REPO_PATH = '$repo/os/$arch'
SORTING_DEFAULTS = {
    'url': '',
    'protocol': '~',
    'last_sync': '~',
    'completion_pct': 0,
    'delay': float('inf'),
    'duration_avg': float('inf'),
    'duration_stddev': float('inf'),
    'score': float('inf'),
    'country': '~',
    'country_code': '~'
}


class Country(NamedTuple):
    """Represents information about countries."""

    name: str
    code: str

    def __str__(self):
        return f'{self.name} ({self.code})'


def valid_mirrors(mirrors: Iterator[dict]) -> Iterator[dict]:
    """Yields valid mirrors."""

    for mirror in mirrors:
        if mirror.get('url'):
            yield mirror
        else:
            LOGGER.warning('Skipping mirror without URL.')


def counted_mirrors(mirrors: Iterator[dict]) -> Iterator[dict]:
    """Yields and counts available mirrors."""

    count = 0

    for count, mirror in enumerate(valid_mirrors(mirrors), start=1):
        yield mirror

    LOGGER.debug('Received %i available mirrors.', count)


def get_mirrors() -> Iterator[dict]:
    """Returns the mirrors from the respective URL."""

    with urlopen(MIRRORS_URL) as response:
        json = load(response)

    return counted_mirrors(json['urls'])


def mirror_url(url: str) -> str:
    """Returns a mirror list URL."""

    scheme, netloc, path, params, query, fragment = urlparse(url)

    if not path.endswith('/'):
        path += '/'

    path += REPO_PATH
    return urlunparse((scheme, netloc, path, params, query, fragment))


def get_lines(mirrors: Iterable[dict], config: Configuration) -> Iterator[str]:
    """Returns a mirror list record."""

    if config.header:
        timestamp = datetime.now().isoformat()
        yield f'# Mirror list generated with speculum on {timestamp}'
        yield '# with configuration:'

        for line in config.lines():
            yield f'#     {line}'

    for mirror in mirrors:
        url = mirror_url(mirror['url'])
        yield f'Server = {url}'


def get_country(mirror: dict) -> Optional[Country]:
    """Returns the mirror's country."""

    if not (country := mirror.get('country')):
        return None

    if not (code := mirror.get('country_code')):
        return None

    return Country(country, code)


def get_countries(mirrors: Iterable[dict]) -> set[Country]:
    """Returns available countries."""

    return set(filter(None, map(get_country, mirrors)))


def list_countries(mirrors: Iterable[dict], reverse: bool = False) -> None:
    """Lists available countries."""

    iterprint(map(str, sorted(get_countries(mirrors), reverse=reverse)))
