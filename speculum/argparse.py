"""Arguments parsing."""

from argparse import ArgumentParser, Namespace
from pathlib import Path

from speculum.parsers import configfile, hours, positive_int


__all__ = ["parse_args"]


DESCRIPTION = "Yet another Arch Linux mirror list optimizer."


def parse_args() -> Namespace:
    """Returns the parsed arguments."""

    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable more detailed logging"
    )
    meg = parser.add_mutually_exclusive_group()
    meg.add_argument(
        "-S",
        "--list-sortopts",
        action="store_true",
        help="list the available sorting options",
    )
    meg.add_argument(
        "-C",
        "--list-countries",
        action="store_true",
        help="list the available countries",
    )
    parser.add_argument(
        "-H",
        "--header",
        action="store_true",
        help="print a header before list of mirrors",
    )
    parser.add_argument(
        "-f",
        "--config",
        type=configfile,
        metavar="file",
        help="reads settings from the given config file",
    )
    parser.add_argument(
        "-s",
        "--sort",
        nargs="+",
        type=str.casefold,
        metavar="option",
        help="sort by the respective sort options",
    )
    parser.add_argument(
        "-r", "--reverse", action="store_true", help="sort in reversed order"
    )
    parser.add_argument(
        "-c",
        "--countries",
        nargs="+",
        type=str.casefold,
        metavar="country",
        help="match mirrors of these countries",
    )
    parser.add_argument(
        "-p",
        "--protocols",
        nargs="+",
        type=str.casefold,
        metavar="protocol",
        help="match mirrors that use one of the specified protocols",
    )
    parser.add_argument(
        "-a",
        "--max-age",
        type=hours,
        metavar="hours",
        help="match mirrors that are not older that the specified age",
    )
    parser.add_argument(
        "-m",
        "--match",
        metavar="regex",
        help="match mirrors that match the regular expression",
    )
    parser.add_argument(
        "-n",
        "--nomatch",
        metavar="regex",
        help="exclude mirrors that match the regular expression",
    )
    parser.add_argument(
        "-t",
        "--complete",
        action="store_true",
        help="match mirrors that are completely synced",
    )
    parser.add_argument(
        "-u", "--active", action="store_true", help="match active mirrors"
    )
    parser.add_argument(
        "-4", "--ipv4", action="store_true", help="match mirrors that support IPv4"
    )
    parser.add_argument(
        "-6", "--ipv6", action="store_true", help="match mirrors that support IPv6"
    )
    parser.add_argument(
        "-i", "--isos", action="store_true", help="match mirrors that host ISOs"
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=positive_int,
        metavar="n",
        help="limit output to this amount of results",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="file",
        help="write the output to the specified file instead of stdout",
    )
    return parser.parse_args()
