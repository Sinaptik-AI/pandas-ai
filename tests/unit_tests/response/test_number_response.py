from pandasai.core.response.number import NumberResponse


def test_number_response_initialization():
    response = NumberResponse(42, "test_code")
    assert response.type == "number"
    assert response.value == 42
    assert response.last_code_executed == "test_code"


def test_number_response_minimal():
    response = NumberResponse(0)  # Zero instead of None
    assert response.type == "number"
    assert response.value == 0
    assert response.last_code_executed is None


def test_number_response_with_float():
    response = NumberResponse(3.14, "test_code")
    assert response.type == "number"
    assert response.value == 3.14
    assert response.last_code_executed == "test_code"


def test_number_response_with_string_number():
    response = NumberResponse("123", "test_code")
    assert response.type == "number"
    assert response.value == "123"  # Value remains as string
