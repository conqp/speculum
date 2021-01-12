#! /usr/bin/env python3
"""Installation script."""


from setuptools import setup


setup(
    name='speculum',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    author='Richard Neumann',
    author_email='mail@richard-neumann.de',
    python_requires='>=3.8',
    packages=['speculum'],
    entry_points={'console_scripts': ['speculum = speculum.main:main']},
    data_files=[
        ('/etc', ['files/speculum.conf']),
        ('/usr/lib/systemd/system', [
            'files/speculum.service',
            'files/speculum.timer'
        ])
    ],
    url='https://github.com/conqp/speculum',
    license='GPLv3',
    description='Yet another Arch Linux mirror list optimizer.',
    keywords='pacman mirror list mirrorlist optimizer filter'
)
