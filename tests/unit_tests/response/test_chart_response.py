import pytest
from PIL import Image
import base64
import io
from pandasai.core.response.chart import ChartResponse


@pytest.fixture
def sample_base64_image():
    # Create a small test image and convert to base64
    img = Image.new("RGB", (100, 100), color="red")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()
    return f"data:image/png;base64,{base64.b64encode(img_byte_arr).decode('utf-8')}"


@pytest.fixture
def chart_response(sample_base64_image):
    return ChartResponse(sample_base64_image, "test_code")


def test_chart_response_initialization(chart_response):
    assert chart_response.type == "chart"
    assert chart_response.last_code_executed == "test_code"


def test_get_image_from_base64(chart_response):
    img = chart_response._get_image()
    assert isinstance(img, Image.Image)
    assert img.size == (100, 100)


def test_get_image_from_file(tmp_path):
    # Create a test image file
    img_path = tmp_path / "test.png"
    img = Image.new("RGB", (100, 100), color="blue")
    img.save(img_path)

    response = ChartResponse(str(img_path), "test_code")
    loaded_img = response._get_image()
    assert isinstance(loaded_img, Image.Image)
    assert loaded_img.size == (100, 100)


def test_save_image(chart_response, tmp_path):
    output_path = tmp_path / "output.png"
    chart_response.save(str(output_path))
    assert output_path.exists()

    # Verify the saved image
    saved_img = Image.open(output_path)
    assert isinstance(saved_img, Image.Image)
    assert saved_img.size == (100, 100)


def test_str_representation(chart_response, monkeypatch):
    # Mock the show method to avoid actually displaying the image
    shown = False

    def mock_show(*args, **kwargs):
        nonlocal shown
        shown = True

    monkeypatch.setattr(Image.Image, "show", mock_show)

    str_value = str(chart_response)
    assert shown  # Verify show was called
    assert isinstance(str_value, str)
