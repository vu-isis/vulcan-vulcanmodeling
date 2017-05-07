from ming.utils import LazyProperty

from ..base.app import VulcanGMEApp
from ..base.model import VulcanGMEProject

class CPSWTApp(VulcanGMEApp):

    tool_label = 'GME_CPSWT'
    default_mount_label = 'CPSWT Project'
    default_mount_point = 'cpswtproject'
    status = 'beta'

    admin_description = (
        "WebGME applications support domain-specific modeling languages with "
        "custom resources and tooling. This is the CPSWT application."
    )

    @LazyProperty
    def gme_project(self):
        return VulcanGMEProject.query.get(app_config_id=self.config._id)
