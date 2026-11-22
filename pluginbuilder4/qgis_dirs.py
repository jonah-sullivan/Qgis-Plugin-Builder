"""Get the deployment directory for QGIS plugins based on operating system.

deployment_dir is where QGIS 4 looks for plugins in the "default" user
profile. Generated Makefiles deploy there (QGISDIR); a plugin for another
profile has to be copied by hand. Unknown operating systems fall back to the
Linux path.
"""

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
