"""Different platforms."""

from logging import DEBUG, WARNING, basicConfig
from platform import machine

from speculum.archlinux import main as archlinux_main
from speculum.archlinuxarm import main as archlinuxarm_main
from speculum.argparse import parse_args
from speculum.logging import LOGGER, LOG_FORMAT


__all__ = ['PLATFORMS', 'main']


PLATFORMS = {
    'x86_64': archlinux_main,
    'armv7l': archlinuxarm_main
}


def main():
    """Filters and sorts the mirrors."""

    args = parse_args()
    basicConfig(level=DEBUG if args.verbose else WARNING, format=LOG_FORMAT)

    try:
        main_func = PLATFORMS[machine()]
    except KeyError:
        LOGGER.critical('Not implemented for "%s".', machine())
        exit(2)

    try:
        exit(main_func())
    except KeyboardInterrupt:
        LOGGER.error('Aborted by user.')
        exit(1)
