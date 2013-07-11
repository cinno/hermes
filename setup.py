# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages

here = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(here, 'requirements.txt')) as req_file:
    requires = req_file.readlines()

setup(
    name='hermes',
    version='0.1',
    packages=find_packages(),
    install_requires=requires,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Intended Audience :: Developers',
        'Environment :: Console',
    ],

    entry_points={
        'console_scripts': [
            'hermes = hermes.cli:main'
        ],

        'hermes.extensions.processors': [
            'printer = hermes.extensions.printer:Printer'
        ]
    },

    zip_safe=False,
    include_package_data=True,
)
