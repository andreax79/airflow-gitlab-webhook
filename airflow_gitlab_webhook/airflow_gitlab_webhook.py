#!/usr/bin/env python

__author__ = 'Andrea Bonomi <andrea.bonomi@italiaonline.it>'
__version__ = '1.0.1'

import os
import os.path
from flask import (Blueprint, request, jsonify)
import flask_admin
import flask_appbuilder
from airflow.plugins_manager import AirflowPlugin
from airflow import configuration
from airflow.www.app import csrf
from airflow.api.common.experimental import trigger_dag
from airflow.exceptions import AirflowException

CONFIG_SECTION = 'gitlab_plugin'
GITLAB_TOKEN = 'X-Gitlab-Token'
MENU_CATEGORY = 'Admin'
MENU_LABEL = 'Gitlab Webhook'
ROUTE = '/webhooks/gitlab'
HTTP_BAD_REQUEST = 400
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404

def get_plugin_config():
    " Return the plugin configuration "
    config = []
    i = 0
    # Iterate over the configurations
    while True:
        suffix = str(i) if i != 0 else '' # the first configuration doesn't have a suffix
        try:
            if not configuration.has_option(CONFIG_SECTION, 'REPOSITORY_URL' + suffix):
                break
        except: # backports.configparser.NoSectionError and friends
            break
        repository_url = configuration.get(CONFIG_SECTION, 'REPOSITORY_URL' + suffix)
        dag = configuration.get(CONFIG_SECTION, 'DAG' + suffix)
        token = configuration.get(CONFIG_SECTION, 'TOKEN' + suffix) if configuration.has_option(CONFIG_SECTION, 'TOKEN' + suffix) else None
        config.append({
            'i': i,
            'repository_url': repository_url,
            'dag_id': dag,
            'token': token
        })
        i = i + 1
    return config

def get_repo_config(repository_url):
    " Get the configuration by repository url "
    for repo_config in plugin_config:
        if repo_config['repository_url'] == repository_url:
            return repo_config
    return None

plugin_config = get_plugin_config() # Plugin configuration

class AbstractGitlabView(object):

    def api(self, event):
        # Parse the request
        try:
            data = request.get_json(force=True)
        except:
            return jsonify({ 'error': 'Malformed request body' }), HTTP_BAD_REQUEST
        # Get the configuration
        repository_url = data['repository']['url']
        repo_config = get_repo_config(repository_url)
        if repo_config is None:
            repository_url = data['repository']['git_http_url']
            repo_config = get_repo_config(repository_url)
        if repo_config is None:
            repository_url = data['repository']['git_ssh_url']
            repo_config = get_repo_config(repository_url)
        if repo_config is None:
            return jsonify({ 'error': 'Repository not found' }), HTTP_NOT_FOUND
        # Check the token
        if repo_config['token'] and repo_config['token'] != request.headers.get(GITLAB_TOKEN):
            return jsonify({ 'error': 'Token authentication failed' }), HTTP_FORBIDDEN
        # Trigger a new dag run
        conf = request.get_json(force=True)
        run_id = None
        try:
            result = trigger_dag.trigger_dag(repo_config['dag_id'], run_id, conf)
            return jsonify({ 'message': str(result) })
        except AirflowException as err:
            return jsonify({ 'error': str(err) }), err.status_code


# Flash Admin
class AdminGitlabView(flask_admin.BaseView, AbstractGitlabView):

    @flask_admin.expose('/')
    def index(self):
        return self.render('index_admin.html', plugin_config=plugin_config)

    @csrf.exempt # exempt the CSRF token
    @flask_admin.expose('/push', methods=[ 'POST' ])
    def push(self):
        return self.api('push')

admin_view = AdminGitlabView(
    url=ROUTE,
    category=MENU_CATEGORY,
    name=MENU_LABEL
)

# AppBuilder (Airflow >= 1.10 and rbac = True)
class AppBuilderGitlabView(flask_appbuilder.BaseView, AbstractGitlabView):
    template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    route_base = ROUTE
    base_permissions = ['can_list']

    @flask_appbuilder.expose("/")
    @flask_appbuilder.has_access
    def list(self):
        return self.render_template('index_appbuilder.html', plugin_config=plugin_config)

    @csrf.exempt # exempt the CSRF token
    @flask_appbuilder.expose('/push', methods=[ 'POST' ])
    def push(self):
        return self.api('push')

appbuilder_gitlab_view = AppBuilderGitlabView()
appbuilder_view = {
    'category': MENU_CATEGORY,
    'name': MENU_LABEL,
    'view': appbuilder_gitlab_view
}

# Blueprint
gitlab_plugin_blueprint = Blueprint(
    'gitlab_plugin_blueprint',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/'
)

# Plugin
class GitlabPlugin(AirflowPlugin):
    name = 'gitlab_plugin'
    operators = []
    flask_blueprints = [gitlab_plugin_blueprint]
    hooks = []
    executors = []
    admin_views = [admin_view]
    menu_links = []
    appbuilder_views = [appbuilder_view]

# AppBuilder (rbac) CSRF exempt workaround
try:
    from airflow.www_rbac.app import csrf as rbac_csrf
    if rbac_csrf is not None:
        appbuilder_gitlab_location = '%s.%s' % (appbuilder_gitlab_view.__module__, 'push')
        rbac_csrf.exempt(appbuilder_gitlab_location)
except:
    pass

