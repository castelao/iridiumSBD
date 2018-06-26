#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""The setup script."""

from setuptools import setup, find_packages
from io import open

with open('README.rst', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst', encoding='utf-8') as history_file:
    history = history_file.read()

with open('requirements.txt', encoding='utf-8') as f:
    requirements = f.read()

setup_requirements = [
    'pytest-runner',
    # TODO(castelao): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='iridiumSBD',
    version='0.0.8',
    description="Communication system for Iridium Short Burst Data Service.",
    long_description=readme + '\n\n' + history,
    author="Guilherme Castelão",
    author_email='guilherme@castelao.net',
    url='https://github.com/castelao/isbd',
    packages=[
        'iridiumSBD',
        'iridiumSBD.directip',
        ],
    entry_points={
        'console_scripts': [
            'iridiumSBD=iridiumSBD.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="BSD license",
    zip_safe=False,
    keywords='isbd',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
