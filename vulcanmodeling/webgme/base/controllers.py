from datetime import datetime, timedelta
import jwt
from jwt.contrib.algorithms.pycrypto import RSAAlgorithm
import logging
from os.path import isfile
import re
import requests
import urllib

from webob import exc
from pylons import tmpl_context as c, app_globals as g, request
from tg import expose, config
from tg.controllers import RestController
from tg.decorators import with_trailing_slash

from vulcanforge.auth.model import User
from vulcanforge.common.controllers import BaseController

LOG = logging.getLogger(__name__)


class VulcanGMEAPIBase(object):

    def __init__(self, tool):
        self.secret = self.get_key(tool.lower())
        self.url = self.get_url(tool.lower())
        self.algorithm = "RS256"
        self.jwt = jwt.PyJWT()
        try:
            self.jwt.register_algorithm(
                'RS256', RSAAlgorithm(RSAAlgorithm.SHA256))
        except ValueError as e:
            if e.message != "Algorithm already has a handler.":
                raise
        self.duration = timedelta(hours=2)

    @staticmethod
    def get_key(name):
        path = config.get("{}.jwt.privatekey".format(name), None)
        if path and isfile(path):
            with open(path) as f:
                return f.read()

    @staticmethod
    def get_url(name):
        url = config.get("{}.host".format(name), None)
        if url and not url.startswith('http'):
            url = "http://" + url
        return url

    def generate_admin_token(self):
        payload = dict(exp=datetime.utcnow()+self.duration,
                       userId='admin')
        token = self.jwt.encode(
            payload, self.secret, algorithm=self.algorithm)
        return token

    def generate_token(self, user):
        payload = dict(exp=datetime.utcnow()+self.duration,
                       userId=user.username)
        token = self.jwt.encode(
            payload, self.secret, algorithm=self.algorithm)
        return token

    def create_project(self, project, app, user):
        g.security.require_access(app, 'admin', user=user)
        nbhd = project.neighborhood.url_prefix[1:-1]
        org = "{}_{}".format(nbhd, project.shortname)
        token = self.generate_admin_token()
        headers = {'Authorization': 'Bearer {}'.format(token)}
        project_name = app.config.options['mount_point']
        seed = app.config.options.get('seed_project')
        payload = dict(type='file', seedName=seed)
        msg = "Creating WebGME project '{}+{}' using seed named '{}'."
        LOG.info(msg.format(org, project_name, seed))
        url = self.url + "/api/projects/{}/{}".format(org, project_name)
        r = requests.put(url, data=payload, headers=headers)
        if not r.ok:
            LOG.warn('Unable to create WebGME project.')

    def delete_project(self, project, app, user):
        g.security.require_access(app, 'admin', user=user)
        token = self.generate_admin_token()
        headers = {'Authorization': 'Bearer {}'.format(token)}
        nbhd = project.neighborhood.url_prefix[1:-1]
        org = "{}_{}".format(nbhd, project.shortname)
        project_name = app.config.options['mount_point']
        url = self.url + "/api/projects/{}/{}".format(org, project_name)
        r = requests.delete(url, headers=headers)
        if not r.ok:
            LOG.warn('Unable to delete WebGME project.')

    def get_seed_projects(self):
        token = self.generate_admin_token()
        headers = {'Authorization': 'Bearer {}'.format(token)}
        url = self.url + "/api/seeds"
        r = requests.get(url, headers=headers)
        if not r.ok:
            LOG.warn("Unable to get WebGME seed projects.")
            return None
        return r.json()


class VulcanGMERootController(VulcanGMEAPIBase, BaseController):

    @with_trailing_slash
    @expose('jinja:vulcanmodeling.webgme.base:templates/index.html')
    def index(self, project=None, obj=None, branch=None, **kwargs):
        # jwt auth token
        token = self.generate_token(c.user)
        # project_name
        nbhd = c.project.neighborhood.url_prefix[1:-1]
        org = "{}_{}".format(nbhd, c.project.shortname)
        name = "{}+{}".format(org, c.app.config.options['mount_point'])
        # query string
        query = dict(project=name, token=token)
        webgme_url = self.url + '?' + urllib.urlencode(query)
        return {
            'webgme_url': webgme_url,
            'hide_sidebar': True,
            'hide_header': True,
            'hide_linkbin': True,
            'hide_chat': True,
        }


class VulcanGMEAuthController(RestController):

    USERNAME_VALIDATOR = re.compile("^[a-z][a-z0-9-]{2,31}$")

    def __init__(self, tool):
        item = "auth.{}.token".format(tool.lower())
        self.token = config.get(item)

    def _before(self, *args, **kw):
        token = request.headers.get('WS-TOKEN')
        if not token or token != self.token:
            LOG.warn("Invalid web service token: '{}'".format(token))
            raise exc.HTTPNotFound()

    @expose('json')
    def get(self, username):
        perms = ('read', 'write', 'delete')
        permissions = {x: False for x in perms}
        if self.USERNAME_VALIDATOR.match(username):
            user = User.by_username(username)
            if user:
                has_access = g.security.has_access
                ac = c.app.config
                for perm in perms:
                    permissions[perm] = has_access(ac, perm, user=user)
        return permissions
