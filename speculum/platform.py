"""Cross-platform implementation."""

from logging import DEBUG, WARNING, basicConfig
from platform import machine

from speculum.archlinux import main as archlinux_main
from speculum.archlinuxarm import main as archlinuxarm_main
from speculum.argparse import parse_args
from speculum.logging import LOGGER, LOG_FORMAT


__all__ = ['PLATFORMS', 'main']


PLATFORMS = {
    'x86_64': archlinux_main,
    'arm': archlinuxarm_main
}


def main():
    """Filters and sorts the mirrors."""

    args = parse_args()
    basicConfig(level=DEBUG if args.verbose else WARNING, format=LOG_FORMAT)
    platform = machine()

    if platform.startswith('arm'):
        platform = 'arm'

    try:
        exit_code = PLATFORMS[platform](args)
    except (KeyError, NotImplementedError):
        LOGGER.critical('Not implemented for "%s".', machine())
        exit(2)
    except KeyboardInterrupt:
        LOGGER.error('Aborted by user.')
        exit(1)

    exit(exit_code)
