import logging
from ming.odm import ThreadLocalODMSession
from pylons import tmpl_context as c

from vulcanforge.common.app import Application
from vulcanforge.notification.model import Notification
from vulcanforge.taskd import task

LOG = logging.getLogger(__name__)


@task
def init(**kwargs):
    from vulcanmodeling.webgme.base.controllers import VulcanGMEAPIBase
    api = VulcanGMEAPIBase(c.app.tool_label)
    api.create_project(c.project, c.app, c.user)
    subject_text = "{} project {} created by {}"
    subject = subject_text.format(c.app.tool_label.replace("_", " "),
                                  c.app.config.options['mount_label'],
                                  c.user.get_pref('display_name'))
    Notification.post_user(
        c.user, c.app.gme_project, 'created', text='WebGME Project created',
        subject=subject
    )
    ThreadLocalODMSession.flush_all()

@task
def uninstall(**kwargs):
    from vulcanmodeling.webgme.base.controllers import VulcanGMEAPIBase
    api = VulcanGMEAPIBase(c.app.tool_label)
    api.delete_project(c.project, c.app, c.user)
    subject_text = "{} project {} deleted by {}"
    subject = subject_text.format(c.app.tool_label.replace("_", " "),
                                  c.app.config.options['mount_label'],
                                  c.user.get_pref('display_name'))
    Notification.post_user(
        c.user, c.app.gme_project, 'created', text='WebGME Project deleted',
        subject=subject
    )
    ThreadLocalODMSession.flush_all()
    Application.uninstall(c.app, project=c.project)
