NAMESPACED_STATIC_DIRS = {
    "webgme": ["vulcanmodeling:webgme/base/static"]
}

MODELING_TOOL_SPEC = {
    "gme_cpswt": {
        "app_path": "vulcanmodeling.webgme.cpswt.app:CPSWTApp",
        "installable": False

    },
    "gme_generic": {
        "app_path": "vulcanmodeling.webgme.generic.app:GenericApp",
        "installable": False
    }
}
