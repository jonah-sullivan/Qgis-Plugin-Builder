"""Get the deployment directory for QGIS plugins based on operating system"""

import os
import platform

_qgis_dir_location = {
    "Linux": ".local/share/QGIS/QGIS4/profiles/default/python/plugins",
    "Windows": "AppData/Roaming/QGIS/QGIS4/profiles/default/python/plugins",
    "Darwin": "Library/Application Support/QGIS/QGIS4/profiles/default/python/plugins",
}

deployment_dir = os.path.join(
    os.path.expanduser("~"), _qgis_dir_location[platform.system()]
)
