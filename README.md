# Airflow Gitlab Webhook Plugin

### Description

A plugin for [Apache Airflow](https://github.com/apache/airflow) that exposes REST endpoint for [Gitlab Webhooks](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html).

### System Requirements

* Airflow Versions
    * 1.10.2 or newer

### Deployment Instructions

1. Install the plugin

    pip install airflow-gitlab-webhook

2. Update the airflow.cfg configuration file adding the *gitlab_plugin* section

        [gitlab_plugin]
        
        repository_url = http://example.com/mike/diaspora.git
        token = 62b32508-b1ad-44d2-97d1-80021a8d7576
        dag = tutorial
        
        (Optional) Configure other repositories
        repository_url1 = http://example.com/bla.git
        token1 = my-secret
        dag1 = git_update

    * repository_url = Gitlab repository URL
    * token = Optional Secure Token
    * dag = DAG to be run when the push even is received
 
3. Configure Gitlab Webook (push event) for the repository

    * https://docs.gitlab.com/ee/user/project/integrations/webhooks.html
 
4. Restart the Airflow Web Server

#### Endpoints

##### push

  * Gitlab Push Event
  
    POST - https://{HOST}:{PORT}/webhooks/gitlab/push

