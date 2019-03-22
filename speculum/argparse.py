"""Arguments parsing."""

from argparse import ArgumentParser, Namespace
from pathlib import Path

from speculum.parsers import hours, posint, regex


__all__ = ['parse_args']


DESCRIPTION = 'Yet another Arch Linux mirrorlist optimizer.'


def parse_args() -> Namespace:
    """Returns the parsed arguments."""

    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='enable more detailed logging')
    parser.add_argument(
        '-S', '--list-sortopts', action='store_true',
        help='list the available sorting options')
    parser.add_argument(
        '-C', '--list-countries', action='store_true',
        help='list the available countries')
    parser.add_argument(
        '-s', '--sort', nargs='+', metavar='<option>',
        help='sort by the respective sort options')
    parser.add_argument(
        '-r', '--reverse', action='store_true', help='sort in reversed order')
    parser.add_argument(
        '-c', '--countries', nargs='+', type=lambda string: string.lower(),
        metavar='<country>', help='match mirrors of these countries')
    parser.add_argument(
        '-p', '--protocols', nargs='+', metavar='<protocol>',
        help='match mirrors that use one of the specified protocols')
    parser.add_argument(
        '-a', '--max-age', type=hours, metavar='hours',
        help='match mirrors that use one of the specified protocols')
    parser.add_argument(
        '-m', '--match', type=regex, metavar='regex',
        help='match mirrors that match the regular expression')
    parser.add_argument(
        '-n', '--nomatch', type=regex, metavar='regex',
        help='exclude mirrors that match the regular expression')
    parser.add_argument(
        '-t', '--complete', action='store_true',
        help='match mirrors that are completely synced')
    parser.add_argument(
        '-u', '--active', action='store_true', help='match active mirrors')
    parser.add_argument(
        '-4', '--ipv4', action='store_true',
        help='match mirrors that support IPv4')
    parser.add_argument(
        '-6', '--ipv6', action='store_true',
        help='match mirrors that support IPv6')
    parser.add_argument(
        '-i', '--isos', action='store_true',
        help='match mirrors that host ISOs')
    parser.add_argument(
        '-l', '--limit', type=posint, metavar='n',
        help='limit output to this amount of results')
    parser.add_argument(
        '-o', '--output', type=Path, metavar='file',
        help='write the output to the specified file instead of stdout')
    args = parser.parse_args()

    if args.list_sortopts and args.list_countries:
        parser.error('Listing of options and countries is mutually exclusive.')

    return args
