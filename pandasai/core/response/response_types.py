import base64
import json
from typing import Any

import pandas as pd
from PIL import Image


class Base:
    """
    Base class for different types of response values.
    """

    def __init__(self, result: dict):
        if not isinstance(result, dict):
            raise ValueError(
                "Expected a dictionary result, but got {type(result).__name__}."
            )
        self.result = result
        self.value = result.get("value")

    def __str__(self) -> str:
        """Return the string representation of the response."""
        return str(self.value)

    def __repr__(self) -> str:
        """Return a detailed string representation for debugging."""
        return f"{self.__class__.__name__}(type={self.result.get('type')!r}, value={self.value!r})"

    def to_dict(self) -> dict:
        """Return a dictionary representation."""
        return self.result

    def to_json(self) -> str:
        """Return a JSON representation."""
        return json.dumps(self.to_dict())

    def get_value(self) -> Any:
        """Return the value from the result."""
        return self.value


class String(Base):
    """
    Class for handling string responses.
    """

    def __init__(self, result: dict):
        super().__init__(result)


class Number(Base):
    """
    Class for handling numerical responses.
    """

    def __init__(self, result: dict):
        super().__init__(result)


class DataFrame(Base):
    """
    Class for handling DataFrame responses.
    """

    def __init__(self, result: dict):
        result["value"] = self.format_value(result["value"])
        super().__init__(result)

    def format_value(self, value):
        if isinstance(value, dict):
            return pd.Dataframe(value)
        return value

    def to_csv(self, file_path: str) -> None:
        self.value.to_csv(file_path, index=False)

    def to_excel(self, file_path: str) -> None:
        self.value.to_excel(file_path, index=False)

    def head(self, n: int = 5) -> pd.DataFrame:
        return self.value.head(n)

    def tail(self, n: int = 5) -> pd.DataFrame:
        return self.value.tail(n)

    def to_json(self):
        json_data = json.loads(self.value.to_json(orient="split", date_format="iso"))
        self.result["value"] = {
            "headers": json_data["columns"],
            "rows": json_data["data"],
        }
        return self.result

    def to_dict(self) -> dict:
        self.result["value"] = self.value.to_dict(orient="split", date_format="iso")
        return self.result


class Chart(Base):
    def __init__(self, result: dict):
        super().__init__(result)

    def show(self):
        img = Image.open(self.value)
        img.show()

    def to_dict(self):
        with open(self.value["value"], "rb") as image_file:
            image_data = image_file.read()

        # Encode the image data to Base64
        self.result[
            "value"
        ] = f"data:image/png;base64,{base64.b64encode(image_data).decode()}"

        return self.result
