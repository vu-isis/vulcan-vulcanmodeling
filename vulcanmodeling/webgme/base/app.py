import logging

import ew.jinja2_ew as ew
from ming.odm import ThreadLocalODMSession
from pylons import tmpl_context as c, app_globals as g

from vulcanforge.common.app import Application
from vulcanforge.common.tool import ConfigOption, SitemapEntry
from vulcanforge.common.util import push_config

from controllers import (
    VulcanGMEAPIBase,
    VulcanGMERootController,
    VulcanGMEAuthController
)
from model import VulcanGMEProject
import tasks as gme_tasks

LOG = logging.getLogger(__name__)


class VulcanGMEApp(Application):

    tool_label = 'WebGME'
    default_mount_label = 'WebGME'
    default_mount_point = 'webgme'
    ordinal = 2
    icons = {
        24: 'webgme/images/webgme_24.png',
        32: 'webgme/images/webgme_32.png',
        48: 'webgme/images/webgme_48.png'
    }
    reference_opts = dict(Application.reference_opts, can_reference=True)
    gme_project = None  # override with a property in child class
    admin_description = (
        "Use WebGME to create your own "
        "Domain Specific Modeling Language (DSML)."
    )
    admin_actions = {"View Project": {"url": ""}}
    config_options = Application.config_options + [
        ConfigOption('seed_project', str, None)
    ]

    def __init__(self, project, config):
        self.root = VulcanGMERootController(self.tool_label)
        self.api_root = VulcanGMEAuthController(self.tool_label)
        Application.__init__(self, project, config)

    @classmethod
    def permissions(cls):
        perms = dict(
            admin='Administer permissions and delete',
            write='WebGME write permission',
            read='WebGME read permission',
            delete='WebGME delete permission'
        )
        return perms

    @classmethod
    def default_acl(cls):
        acl = super(VulcanGMEApp, cls).default_acl()
        acl['Developer'] = ['read', 'write', 'delete']
        return acl

    @classmethod
    def get_seed_projects(cls):
        api = VulcanGMEAPIBase(cls.tool_label)
        return api.get_seed_projects()

    @classmethod
    def get_install_option_fields(cls, neighborhood):
        fields = []
        seed_projects = cls.get_seed_projects()
        if seed_projects:
            seed_options = [
                ew.Option(label=seed, value=seed, html_value=seed)
                for seed in seed_projects
            ]
            fields.append(ew.SingleSelectField(label="Seed project",
                                               name='seed_project',
                                               options=seed_options))
        return fields

    def main_menu(self):
        """
        Apps should provide their entries to be added to the main nav

        :return: a list of :class:`SitemapEntries <vulcanforge.common.types.SitemapEntry>`

        """
        return [SitemapEntry(self.config.options.mount_label.title(), '.')]

    @property
    def sitemap(self):
        menu_id = self.config.options.mount_label.title()
        with push_config(c, app=self):
            return [
                SitemapEntry(menu_id, '.')[self.sidebar_menu()] ]

    def admin_menu(self):
        admin_url = c.project.url() + 'admin/' +\
                    self.config.options.mount_point + '/'
        links = []
        if self.permissions and g.security.has_access(self, 'admin'):
            links.append(
                SitemapEntry(
                    'Permissions',
                    admin_url + 'permissions',
                    className='nav_child'
                )
            )
        return links

    def install(self, project, acl=None):
        super(VulcanGMEApp, self).install(project, acl=acl)
        VulcanGMEProject.upsert(
            name=self.config.options['mount_point'],
            app=self.tool_label
        )
        ThreadLocalODMSession.flush_all()
        gme_tasks.init.post()

    def uninstall(self, project=None, project_id=None):
        gme_tasks.uninstall.post()
