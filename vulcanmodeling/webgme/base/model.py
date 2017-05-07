from pymongo.errors import DuplicateKeyError
from ming.odm import FieldProperty
from vulcanforge.artifact.model import Artifact


class VulcanGMEProject(Artifact):
    class __mongometa__:
        name = "gme_project"
        unique_indexes = ['name', 'app']

    name = FieldProperty(str)
    app = FieldProperty(str)

    @classmethod
    def upsert(cls, name, app, **kwargs):
        gme_project = cls.query.get(name=name, app=app)
        if not gme_project:
            gme_project = cls(name=name, app=app, **kwargs)
        return gme_project

    def url(self):
        return self.app_config.url()
