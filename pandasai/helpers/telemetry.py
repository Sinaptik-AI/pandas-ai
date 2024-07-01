import os
import platform

import requests

from pandasai.__version__ import __version__


def scarf_analytics():
    try:
        if (
            os.getenv("SCARF_NO_ANALYTICS") != "true"
            and os.getenv("DO_NOT_TRACK") != "true"
        ):
            requests.get(
                "https://package.pandabi.ai/pandasai-telemetry?version="
                + __version__
                + "&platform="
                + platform.system()
            )
    except Exception:
        pass
