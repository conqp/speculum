"""Tests the limiting module."""

from unittest import TestCase

from speculum.limiting import limit


class TestLimit(TestCase):
    """Tests the limit() function."""

    def setUp(self):
        """Sets example iterables."""
        self.iterable = [1, 2.0, 3, 'foo', 'bar', {'spamm': 'eggs'}]

    def test_limit(self):
        """Tests the limit function."""
        for maxlen in range(len(self.iterable)):
            self.assertSequenceEqual(
                list(limit(self.iterable, maxlen)),
                self.iterable[:maxlen]
            )

        self.assertSequenceEqual(
            list(limit(self.iterable, None)),
            self.iterable
        )
