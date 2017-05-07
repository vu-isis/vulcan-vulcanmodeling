from ming.utils import LazyProperty

from ..base.app import VulcanGMEApp
from ..base.model import VulcanGMEProject

class GenericApp(VulcanGMEApp):

    tool_label = 'GME_Generic'
    default_mount_label = 'WebGME Project'
    default_mount_point = 'webgmeproject'
    status = 'production'

    admin_description = (
        "WebGME applications support domain-specific modeling languages with "
        "custom resources and tooling. This is the Generic "
        "multi-domain application."
    )

    @LazyProperty
    def gme_project(self):
        return VulcanGMEProject.query.get(app_config_id=self.config._id)
