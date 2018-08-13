#!/usr/bin/env python
from setuptools import setup, find_packages
import fastentrypoints

setup(
    name='flik',
    version='1.0',
    description='blueant cli client',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    entry_points={'console_scripts': ['flik = flik.flik:main']},
    install_requires=[
        'python-dateutil >= 2.7.3',
        'zeep >= 3.1.0',
        'pyyaml >= 3.13',
        'keyring >= 13.2.1',
        'keyrings.alt >= 3.1',
        'pendulum >= 2.0.3'
    ],
    zip_safe=False)
