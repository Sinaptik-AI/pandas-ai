import base64
import io
from typing import Any

from PIL import Image

from .base import BaseResponse


class ChartResponse(BaseResponse):
    def __init__(self, value: Any, last_code_executed: str):
        super().__init__(value, "chart", last_code_executed)

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

    def get_base64_image(self) -> str:
        img = self._get_image()
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="PNG")
        img_byte_arr = img_byte_arr.getvalue()
        return base64.b64encode(img_byte_arr).decode("utf-8")
