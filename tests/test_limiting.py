"""Tests the limiting module."""

from json import load
from pathlib import Path
from unittest import TestCase

from speculum.limiting import limit


class TestLimit(TestCase):
    """Tests the limit() function."""

    def setUp(self):
        """Sets example iterables."""
        with Path(__file__).parent.joinpath('mirrors.json').open() as file:
            json = load(file)

        self.mirrors = json['urls']

    def test_limit(self):
        """Tests the limit function."""
        for maxlen in range(len(self.mirrors)):
            self.assertSequenceEqual(
                list(limit(self.mirrors, maxlen)),
                self.mirrors[:maxlen]
            )

        self.assertSequenceEqual(
            list(limit(self.mirrors, None)),
            self.mirrors
        )
