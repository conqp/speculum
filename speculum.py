#!/usr/bin/env python3
#
#  speculum - An Arch Linux mirror list updater.
#
#  Copyright (C) 2019 Richard Neumann <mail at richard dash neumann period de>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""speculum.

    Yet another Arch Linux mirrorlist optimizer.

Usage:
    speculum [options]
    
Options:
    --help, -h              Show this page.
"""
from datetime import datetime
from urllib.parse import urlparse, ParseResult


class Duration(NamedTuple):
    """Represents the duration data on a mirror."""
    
    average: float
    stddev: float
    
    
class Country(NamedTuple):
    """Represents country information."""
    
    name: str
    code: str
    
    def match(self, string):
        """Matches a country description."""
        return str.lower() in (self.name.lower(), self.code.lower())


class Mirror(NamedTuple):
    """Represents information about a mirror."""
    
    url: ParseResult
    last_sync: datetime
    completion: float
    delay: int
    duration: Duration
    score: float
    active: bool
    country: Country
    isos: bool
    
