#!/usr/bin/env python
import os
import os.path
import re
from setuptools import (find_packages, setup)

VERSION_RE = re.compile('__version__\s*=\s*[\'"](.*)[\'"]')

def get_version():
    with open(os.path.join(
          os.path.dirname(os.path.abspath(__file__)),
          'airflow_gitlab_webhook/airflow_gitlab_webhook.py')) as f:
        for line in f:
            match = VERSION_RE.match(line)
            if match:
                return match.group(1)
    raise Exception

with open('README.md', 'r') as f:
    long_description = f.read()

with open('requirements.txt', 'r') as f:
    install_requires = f.read().split('\n')

setup(
    name='airflow_gitlab-webhook',
    version=get_version(),
    packages=find_packages(),
    include_package_data=True,
    package_data={ 'airflow_gitlab_webhook': [ 'templates/*.html' ] },
    entry_points = {
        'airflow.plugins': [
            'airflow_gitlab_webhook = airflow_gitlab_webhook.airflow_gitlab_webhook:GitlabPlugin'
        ]
    },
    zip_safe=False,
    url='https://github.com/andreax79/airflow-gitlab-webhook',
    author='Andrea Bonomi',
    author_email='andrea.bonomi@gmail.com',
    description='Apache Airflow Gitlab Webhook integration',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=install_requires,
    license='Apache License, Version 2.0',
    classifiers=[
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
    ]
)

