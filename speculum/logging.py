"""Logging."""

from logging import getLogger


__all__ = ['LOGGER', 'LOG_FORMAT']


LOGGER = getLogger('speculum')
LOG_FORMAT = '[%(levelname)s] %(name)s: %(message)s'
