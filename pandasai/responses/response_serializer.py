import base64
import json

import pandasai.pandas as pd
from pandasai.responses.response_type import ResponseType


class ResponseSerializer:
    @staticmethod
    def serialize_dataframe(df: pd.DataFrame):
        json_data = json.loads(df.to_json(orient="split", date_format="iso"))
        return {"headers": json_data["columns"], "rows": json_data["data"]}

    @staticmethod
    def serialize(result: ResponseType) -> ResponseType:
        """
        Format output response
        Args:
            result (ResponseType): response returned after execution

        Returns:
            ResponseType: formatted response output
        """
        if result["type"] == "dataframe":
            df_dict = ResponseSerializer.serialize_dataframe(result["value"])
            return {"type": result["type"], "value": df_dict}

        elif result["type"] == "plot":
            with open(result["value"], "rb") as image_file:
                image_data = image_file.read()
            # Encode the image data to Base64
            base64_image = (
                f"data:image/png;base64,{base64.b64encode(image_data).decode()}"
            )
            return {
                "type": result["type"],
                "value": base64_image,
            }
        else:
            return result
