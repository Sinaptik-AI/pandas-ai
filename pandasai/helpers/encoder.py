from json import JSONEncoder

import numpy as np


class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        # Let the base class default method raise the TypeError
        return JSONEncoder.default(self, obj)
