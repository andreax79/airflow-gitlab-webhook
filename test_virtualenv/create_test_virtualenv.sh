#!/usr/bin/env bash
cd "$(dirname "$0")"
source ./mo.sh
export AIRFLOW_HOME=${PWD}

#export AIRFLOW_VERSION=1.10.4rc3
export AIRFLOW_VERSION=1.10.3

virtualenv -p `which python3` .
echo "export AIRFLOW_HOME=${AIRFLOW_HOME}" >> bin/activate
source bin/activate
pip install --upgrade pip
pip install pendulum==1.4.4
AIRFLOW_GPL_UNIDECODE=true pip install apache-airflow[crypto,password]==${AIRFLOW_VERSION}
# AIRFLOW_GPL_UNIDECODE=true pip install apache-airflow==${AIRFLOW_VERSION}

if [[ $AIRFLOW_VERSION == "1.10.3" ]]; then # killme
    # Apache Airflow : airflow initdb throws ModuleNotFoundError: No module named 'werkzeug.wrappers.json'; 'werkzeug.wrappers' is not a package error
    # https://stackoverflow.com/questions/56933523/apache-airflow-airflow-initdb-throws-modulenotfounderror-no-module-named-wer
    pip install -U Flask==1.0.4
    # pip install werkzeug==0.15.5
fi

pip install --no-deps  airflow-gitlab-webhook

mo -u < airflow.cfg.tmpl > airflow.cfg
airflow initdb
