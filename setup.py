#!/usr/bin/env python2
from setuptools import setup, find_packages
import fastentrypoints

setup(
    name='flik',
    version='0.10',
    description='blue ant cli client',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    entry_points={'console_scripts': ['flik = flik.flik:main']},
    install_requires=[
        'python-dateutil',
        'zeep',
        'pyyaml',
        'keyring',
        'keyrings.alt'
    ],
    zip_safe=False)
