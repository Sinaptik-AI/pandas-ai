from pandasai.core.response.error import ErrorResponse


def test_error_response_initialization():
    response = ErrorResponse(
        "test error", last_code_executed="test_code", error="test error message"
    )
    assert response.type == "error"
    assert response.value == "test error"
    assert response.last_code_executed == "test_code"
    assert response.error == "test error message"


def test_error_response_minimal():
    response = ErrorResponse()
    assert response.type == "error"
    assert (
        response.value
        == "Unfortunately, I was not able to get your answer. Please try again."
    )
    assert response.last_code_executed is None
    assert response.error is None


def test_error_response_with_only_value():
    response = ErrorResponse("Custom error message")
    assert response.type == "error"
    assert response.value == "Custom error message"
    assert response.last_code_executed is None
    assert response.error is None


def test_error_response_with_non_string_value():
    response = ErrorResponse(123, "test_code", "error message")
    assert response.type == "error"
    assert response.value == 123
    assert response.last_code_executed == "test_code"
    assert response.error == "error message"
