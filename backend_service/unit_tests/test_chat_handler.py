import unittest
from unittest.mock import patch, MagicMock
import json
from chat_handler import lambda_handler  # Replace with the correct import path

class TestChatHandler(unittest.TestCase):
    """
    Unit test class for the `lambda_handler` function in `chat_handler.py`.

    Tests various request scenarios to ensure the chat handler correctly authenticates users,
    validates request payloads, interacts with the Bedrock agent, and returns appropriate HTTP responses.
    """

    @patch("chat_handler.jwt.decode")
    @patch("chat_handler.bedrock_agent.invoke_agent")
    def test_successful_chat(self, mock_invoke_agent, mock_jwt_decode):
        """
        Test successful invocation of the chat handler with a valid JWT and input.

        Ensures that the handler:
        - Decodes a valid JWT token.
        - Successfully invokes the Bedrock agent.
        - Returns a 200 response with the agent's message.
        """
        mock_jwt_decode.return_value = {
            "email": "john.doe@example.com",
            "sessionId": "mock-session-id",
            "exp": 9999999999
        }
        mock_invoke_agent.return_value = {
            "completion": [{"chunk": {"bytes": b"Hello, how can I help?"}}]
        }
        event = {
            "httpMethod": "POST",
            "headers": {"authorization": "Bearer valid-jwt-token"},
            "body": json.dumps({"input": "Hello!"})
        }
        context = {}
        response = lambda_handler(event, context)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["response"], "Hello, how can I help?")
        
    @patch("chat_handler.boto3.client")
    @patch("chat_handler.jwt.decode")
    def test_missing_or_invalid_jwt(self, mock_jwt_decode, mock_bedrock_client):
        """
        Test the handler's response when the JWT is missing or invalid.

        Ensures the handler returns a 401 status code and a relevant error message.
        """
        mock_bedrock = MagicMock()
        mock_bedrock_client.return_value = mock_bedrock
        mock_jwt_decode.side_effect = Exception("Invalid token")

        event = {
            "httpMethod": "POST",
            "headers": {"authorization": "Bearer invalid-jwt-token"},
            "body": json.dumps({"input": "Hello!"})
        }
        context = {}
        response = lambda_handler(event, context)

        self.assertEqual(response["statusCode"], 401)
        self.assertIn("error", json.loads(response["body"]))
        self.assertEqual(json.loads(response["body"])["error"], "Invalid token")

    @patch("chat_handler.boto3.client")
    @patch("chat_handler.jwt.decode")
    def test_missing_input_field(self, mock_jwt_decode, mock_bedrock_client):
        """
        Test the handler's behavior when the input field is missing in the request body.

        Expects a 400 status code with a 'Missing input' error message.
        """
        mock_bedrock = MagicMock()
        mock_bedrock_client.return_value = mock_bedrock
        mock_jwt_decode.return_value = {
            "email": "john.doe@example.com",
            "sessionId": "mock-session-id",
            "exp": 9999999999
        }

        event = {
            "httpMethod": "POST",
            "headers": {"authorization": "Bearer valid-jwt-token"},
            "body": json.dumps({})
        }
        context = {}
        response = lambda_handler(event, context)

        self.assertEqual(response["statusCode"], 400)
        self.assertIn("error", json.loads(response["body"]))
        self.assertEqual(json.loads(response["body"])["error"], "Missing 'input' field")

    @patch("chat_handler.boto3.client")
    @patch("chat_handler.jwt.decode")
    def test_missing_session_id_in_jwt(self, mock_jwt_decode, mock_bedrock_client):
        """
        Test behavior when the JWT is valid but missing the required `sessionId` field.

        Ensures the handler returns a 401 with an appropriate error message.
        """
        mock_bedrock = MagicMock()
        mock_bedrock_client.return_value = mock_bedrock
        mock_jwt_decode.return_value = {
            "email": "john.doe@example.com",
            "exp": 9999999999
        }

        event = {
            "httpMethod": "POST",
            "headers": {"authorization": "Bearer valid-jwt-token"},
            "body": json.dumps({"input": "Hello!"})
        }
        context = {}
        response = lambda_handler(event, context)

        self.assertEqual(response["statusCode"], 401)
        self.assertIn("error", json.loads(response["body"]))
        self.assertEqual(json.loads(response["body"])["error"], "Missing session ID in token")

    @patch("chat_handler.bedrock_agent")
    @patch("chat_handler.jwt.decode")
    def test_bedrock_error(self, mock_jwt_decode, mock_bedrock_agent):
        """
        Test the handler's error response when the Bedrock agent fails during invocation.

        Expects a 500 Internal Server Error and an appropriate error message.
        """
        mock_jwt_decode.return_value = {
            "email": "john.doe@example.com",
            "sessionId": "mock-session-id",
            "exp": 9999999999
        }
        mock_bedrock_agent.invoke_agent.side_effect = Exception("Bedrock API error")

        event = {
            "httpMethod": "POST",
            "headers": {"authorization": "Bearer valid-jwt-token"},
            "body": json.dumps({"input": "Hello!"})
        }
        context = {}
        response = lambda_handler(event, context)

        self.assertEqual(response["statusCode"], 500)
        body = json.loads(response["body"])
        self.assertIn("error", body)
        self.assertEqual(body["error"], "Internal server error")

if __name__ == "__main__":
    unittest.main()
