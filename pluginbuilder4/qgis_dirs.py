"""Get the deployment directory for QGIS plugins based on operating system"""

import platform
from pathlib import Path

_qgis_dir_location = {
    "Linux": ".local/share/QGIS/QGIS4/profiles/default/python/plugins",
    "Windows": "AppData/Roaming/QGIS/QGIS4/profiles/default/python/plugins",
    "Darwin": "Library/Application Support/QGIS/QGIS4/profiles/default/python/plugins",
}

deployment_dir = Path.home() / _qgis_dir_location.get(
    platform.system(), _qgis_dir_location["Linux"]
)
