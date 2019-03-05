#! /usr/bin/env python3
"""Install script."""


from distutils.core import setup


setup(
    name='speculum',
    version='1.4.3',
    author='Richard Neumann',
    author_email='<mail at richard dash neumann period de>',
    maintainer='Richard Neumann',
    maintainer_email='<mail at richard dash neumann period de>',
    packages=['speculum'],
    scripts=['files/speculum'],
    description=('Yet another Arch Linux mirror list optimizer.'))
