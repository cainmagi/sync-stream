#!python
# -*- coding: UTF-8 -*-
'''
################################################################
# Installation
# @ Sync-stream
# Lead by Artificial Intelligence Group (AIT), Aramco.
# Produced by
# Yuchen Jin @ cainmagi@gmail.com,
#              yjin4@uh.edu.
# Main Requirements: (Pay attention to version)
#   python 3.6+
#   fasteners 0.16+ (optional)
#   flask 2.0.0+ (optional)
#   flask-restful 0.3.9+ (optional)
#   urllib3 1.26.4+ (optional)
# This module is used for maintaining the installation of the
# package.
################################################################
'''

import setuptools

with open('README.md', 'r') as fh:
    LONG_DESCRIPTION = fh.read()

INSTALL_REQUIRES_FILE = [
    'fasteners>=0.16',
]

INSTALL_REQUIRES_HOST = [
    'flask>=2.0.0',
    'flask-restful>=0.3.9',
    'jinja2>=3.0.0',
    'werkzeug>=2.0.1',
    'urllib3>=1.26.4'
]

setuptools.setup(
    name='syncstream',
    version='0.3.2',
    author='Yuchen Jin',
    author_email='cainmagi@gmail.com',
    description='A python tool for synchronize the messages from different threads, processes or hosts.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/cainmagi/sync-stream',
    project_urls={
        'Tracker': 'https://github.com/cainmagi/sync-stream/issues',
        'Documentation': 'https://cainmagi.github.io/sync-stream/',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    license='MIT',
    keywords=[
        'stdout', 'stdout-redirection', 'multiprocessing', 'synchronization', 'stream',
        'python', 'python3', 'python-library'
    ],
    packages=setuptools.find_packages(),
    install_requires=[],
    extras_require={
        'file': INSTALL_REQUIRES_FILE,
        'host': INSTALL_REQUIRES_HOST,
    },
    python_requires='>=3.6',
)
