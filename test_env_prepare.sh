#!/usr/bin/env bash
# Prepare the Virtualenv
virtualenv test -p python3
cd test
source bin/activate
# Install Apache Airflow
AIRFLOW_GPL_UNIDECODE=1 pip3 install -r ../requirements.txt
AIRFLOW_GPL_UNIDECODE=1 pip install apache-airflow[crypto]
# Fix for Python 3.7
# https://issues.apache.org/jira/browse/AIRFLOW-2941
pip3 install tenacity==4.11.0 --force
# Create airflow home
export AIRFLOW_HOME=$PWD/airflow
airflow
cd airflow
# Patch config file
patch < ../../test_env_airflow.cfg.patch
# Init db and create user
airflow initdb
airflow create_user --username admin --role Admin --email admin@example.com --firstname admin --lastname admin --password admin
# Plugins
mkdir plugins
cd plugins
ln -s ../../../airflow_gitlab_webhook
