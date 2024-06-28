import json
import pytest
from unittest import mock
from services.prompt_builder import prompt
from common.similarity_search_parameters import prepare_similarity_search_request
from models.chat_response import parse_QNAResponse
from services.openai_chat_completion import qna
import azure.functions as func
from main import main

@pytest.fixture
def req():
    """Fixture to mock the HTTP request."""
    req = mock.MagicMock(func.HttpRequest)
    req.get_body.return_value = json.dumps({
        "business_unit": "unit",
        "use_case": "case",
        "top_p": 5,
        "filename": "file",
        "threshold_score": 0.9,
        "collection": "collection",
        "query": "user query"
    }).encode('utf-8')
    return req

@pytest.fixture
def context():
    """Fixture to mock the Azure function context."""
    return mock.MagicMock(func.Context)

@mock.patch('main.prepare_similarity_search_request')
@mock.patch('main.prompt')
@mock.patch('main.qna')
@mock.patch('main.parse_QNAResponse')
def test_main_success(prepare_similarity_search_request_mock, prompt_mock, qna_mock, parse_QNAResponse_mock, req, context):
    """Test successful execution of the main function."""
    # Arrange
    prepare_similarity_search_request_mock.return_value = ([{
        "filename": "file1",
        "page": 1,
        "content": "content1",
        "score": 0.95
    }], "user query")

    prompt_instance = mock.MagicMock()
    prompt_instance.create_prompt.return_value = "prompt_string"
    prompt_mock.return_value = prompt_instance

    qna_instance = mock.MagicMock()
    qna_instance.chat_completion.return_value = "response_string"
    qna_mock.return_value = qna_instance

    parse_QNAResponse_instance = mock.MagicMock()
    parse_QNAResponse_instance.get_response.return_value = {
        "response": "response_string",
        "filename": "file1",
        "passage_id": 1,
        "source_content": "content1",
        "similarity_score": 0.95
    }
    parse_QNAResponse_mock.return_value = parse_QNAResponse_instance

    # Act
    response = main(req, context)

    # Assert
    assert response.status_code == 200
    response_dict = json.loads(response.get_body().decode('utf-8'))
    assert "Response" in response_dict
    assert len(response_dict["Response"]) == 1
    assert response_dict["Response"][0]["response"] == "response_string"

@mock.patch('main.prepare_similarity_search_request')
def test_main_no_results(prepare_similarity_search_request_mock, req, context):
    """Test main function with no search results."""
    # Arrange
    prepare_similarity_search_request_mock.return_value = ([], "user query")

    # Act
    response = main(req, context)

    # Assert
    assert response.status_code == 400
    assert response.get_body().decode('utf-8') == "No chunk has the similarity score more than threshold score"

@mock.patch('main.prepare_similarity_search_request')
@mock.patch('main.prompt')
@mock.patch('main.qna')
@mock.patch('main.parse_QNAResponse')
def test_main_exception_handling(prepare_similarity_search_request_mock, prompt_mock, qna_mock, parse_QNAResponse_mock, req, context):
    """Test main function exception handling."""
    # Arrange
    prepare_similarity_search_request_mock.side_effect = Exception("Test Exception")

    # Act
    response = main(req, context)

    # Assert
    assert response.status_code == 400
    assert response.get_body().decode('utf-8') == "Test Exception"

@pytest.mark.parametrize("request_body, expected_status, expected_response", [
    ({"business_unit": "unit", "use_case": "case", "top_p": 5, "filename": "file", "threshold_score": 0.9, "collection": "collection", "query": "user query"}, 200, "Response"),
    ({"business_unit": "unit", "use_case": "case"}, 400, "No chunk has the similarity score more than threshold score")
])
def test_main_parameterized(request_body, expected_status, expected_response, req, context):
    """Test main function with parameterized inputs."""
    req.get_body.return_value = json.dumps(request_body).encode('utf-8')

    # Mocking dependencies
    with mock.patch('main.prepare_similarity_search_request') as prepare_mock:
        if expected_status == 200:
            prepare_mock.return_value = ([{
                "filename": "file1",
                "page": 1,
                "content": "content1",
                "score": 0.95
            }], "user query")

            with mock.patch('main.prompt') as prompt_mock:
                prompt_instance = mock.MagicMock()
                prompt_instance.create_prompt.return_value = "prompt_string"
                prompt_mock.return_value = prompt_instance

                with mock.patch('main.qna') as qna_mock:
                    qna_instance = mock.MagicMock()
                    qna_instance.chat_completion.return_value = "response_string"
                    qna_mock.return_value = qna_instance

                    with mock.patch('main.parse_QNAResponse') as parse_mock:
                        parse_instance = mock.MagicMock()
                        parse_instance.get_response.return_value = {
                            "response": "response_string",
                            "filename": "file1",
                            "passage_id": 1,
                            "source_content": "content1",
                            "similarity_score": 0.95
                        }
                        parse_mock.return_value = parse_instance

                        response = main(req, context)
        else:
            prepare_mock.return_value = ([], "user query")
            response = main(req, context)

    # Assert
    assert response.status_code == expected_status
    if expected_status == 200:
        response_dict = json.loads(response.get_body().decode('utf-8'))
        assert expected_response in response_dict
    else:
        assert response.get_body().decode('utf-8') == expected_response
