from typing import List

import pandas as pd


class ResponseDeserializer:
    """
    Deserialize chat response
    """

    @staticmethod
    def deserialize(response: List[dict]):
        for output in response:
            if output["type"] == "dataframe":
                output["value"] = pd.DataFrame(
                    output["value"]["rows"], columns=output["value"]["headers"]
                )
            # TODO - handle plot here...

        return response
