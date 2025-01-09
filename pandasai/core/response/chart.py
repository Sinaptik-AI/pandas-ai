from typing import Any
from PIL import Image
import base64
import io

from .base import BaseResponse


class ChartResponse(BaseResponse):
    def __init__(self, result: Any, last_code_executed: str):
        super().__init__(result, "chart", last_code_executed)

    def _get_image(self) -> Image.Image:
        if not self.value.startswith("data:image"):
            return Image.open(self.value)

        base64_data = self.value.split(",")[1]
        image_data = base64.b64decode(base64_data)
        return Image.open(io.BytesIO(image_data))

    def save(self, path: str):
        img = self._get_image()
        img.save(path)

    def show(self):
        img = self._get_image()
        img.show()

    def __str__(self) -> str:
        self.show()
        return self.value
