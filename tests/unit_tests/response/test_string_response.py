from pandasai.core.response.string import StringResponse


def test_string_response_initialization():
    response = StringResponse("test value", "test_code")
    assert response.type == "string"
    assert response.value == "test value"
    assert response.last_code_executed == "test_code"


def test_string_response_minimal():
    response = StringResponse("")
    assert response.type == "string"
    assert response.value == ""
    assert response.last_code_executed is None


def test_string_response_with_non_string_value():
    response = StringResponse(123, "test_code")
    assert response.type == "string"
    assert response.value == 123
    assert response.last_code_executed == "test_code"
