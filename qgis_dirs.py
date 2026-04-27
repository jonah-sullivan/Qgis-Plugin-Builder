"""Get the deployment directory for QGIS plugins based on operating system"""

import os
import platform

try:
    from qgis.core import Qgis

    _qgis_version = "QGIS4" if Qgis.QGIS_VERSION_INT >= 40000 else "QGIS3"
except ImportError:
    _qgis4_dir = os.path.join(os.environ["HOME"], ".local", "share", "QGIS", "QGIS4")
    _qgis_version = "QGIS4" if os.path.isdir(_qgis4_dir) else "QGIS3"

_qgis_dir_location = {
    "QGIS3": {
        "Linux": ".local/share/QGIS/QGIS3/profiles/default/python/plugins",
        "Windows": "AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins",
        "Darwin": "Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins",
    },
    "QGIS4": {
        "Linux": ".local/share/QGIS/QGIS4/profiles/default/python/plugins",
        "Windows": "AppData/Roaming/QGIS/QGIS4/profiles/default/python/plugins",
        "Darwin": "Library/Application Support/QGIS/QGIS4/profiles/default/python/plugins",
    },
}

deployment_dir = os.path.join(
    os.path.expanduser("~"), _qgis_dir_location[_qgis_version][platform.system()]
)
