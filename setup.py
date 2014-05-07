#!/usr/bin/env python

try:
    from setuptools import setup
    from setuptools import find_packages
except ImportError:
    raise ImportError("Could not import \"setuptools\". Please install the setuptools package.")


packages = find_packages(where=".", exclude=('tests', 'bin', 'docs', 'fixtures', 'assets', 'conf', 'deploy'))

requires = []

with open('requirements.txt', 'r') as reqfile:
    for line in reqfile:
        requires.append(line.strip())

classifiers = (
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Enivronment :: No Input/Output (Daemon)',
    'Environment :: MacOS X',
    'Framework :: Celery',
    'Framework :: PyGame',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 2.7',
    'Topic :: Scientific/Engineering :: Artificial Life',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
)

config = {
    "name": "swarm-simulator",
    "version": "1.1",
    "description": "Implements a search and rescue simulation as well as an evolver.",
    "author": "Benjamin Bengfort",
    "author_email": "benjamin@bengfort.com",
    "url": "https://github.com/mclumd/swarm-simulator",
    "packages": packages,
    "install_requires": requires,
    "classifiers": classifiers,
    "zip_safe": False,
    "scripts": ['bin/runsim.py', 'bin/evolver.py'],
}

setup(**config)
