#!/usr/bin/env python2

from setuptools import setup, find_packages

setup(name='flik',
        version='0.1',
        description='blue ant cli client',
        license='MIT',
        packages=find_packages(),
        entry_points={'console_scripts': [
            'flik = flik.flik:main'
            ]},
        install_requires=[
            'python-dateutil',
            'suds',
            'pyyaml'
            ],
        zip_safe=True
        )
