"""Tests the limiting module."""

from json import load
from pathlib import Path
from unittest import TestCase

from speculum.limiting import limit


MIRRORS_FILE = Path(__file__).parent / 'mirrors.json'


class TestLimit(TestCase):
    """Tests the limit() function."""

    def setUp(self):
        """Sets example iterables."""
        with MIRRORS_FILE.open() as file:
            json = load(file)

        self.mirrors = json['urls']

    def test_limit(self):
        """Tests the limit function."""
        for max_len in range(len(self.mirrors)):
            self.assertSequenceEqual(
                list(limit(self.mirrors, max_len)),
                self.mirrors[:max_len]
            )

        self.assertSequenceEqual(
            list(limit(self.mirrors, None)),
            self.mirrors
        )
