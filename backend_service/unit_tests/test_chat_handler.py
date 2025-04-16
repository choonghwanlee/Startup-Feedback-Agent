import unittest
from unittest.mock import patch, MagicMock
import json
from chat_handler import lambda_handler  # Replace with the correct import path

class TestChatHandler(unittest.TestCase):

    @patch("chat_handler.boto3.client")
    @patch("chat_handler.jwt.decode")
    def test_successful_chat(self, mock_jwt_decode, mock_bedrock_client):
        # Setup mocks
        mock_bedrock = MagicMock()
        mock_bedrock_client.return_value = mock_bedrock
        mock_bedrock.invoke_agent.return_value = {
            "completion": [{"chunk": {"bytes": b"Hello, how can I help?"}}]
        }
        mock_jwt_decode.return_value = {
            "email": "john.doe@example.com",
            "sessionId": "mock-session-id",
            "exp": 9999999999
        }

        # Sample event (successful chat)
        event = {
            "httpMethod": "POST",
            "headers": {"Authorization": "Bearer valid-jwt-token"},
            "body": json.dumps({
                "input": "Hello!"
            })
        }
        context = {}

        # Call lambda_handler
        response = lambda_handler(event, context)

        # Asserts
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("response", json.loads(response["body"]))
        self.assertEqual(json.loads(response["body"])["response"], "Hello, how can I help?")
        mock_bedrock.invoke_agent.assert_called_once()

    @patch("chat_handler.boto3.client")
    @patch("chat_handler.jwt.decode")
    def test_missing_or_invalid_jwt(self, mock_jwt_decode, mock_bedrock_client):
        # Setup mocks
        mock_bedrock = MagicMock()
        mock_bedrock_client.return_value = mock_bedrock

        # Simulate invalid JWT
        mock_jwt_decode.side_effect = Exception("Invalid token")

        # Sample event (missing/invalid JWT)
        event = {
            "httpMethod": "POST",
            "headers": {"Authorization": "Bearer invalid-jwt-token"},
            "body": json.dumps({
                "input": "Hello!"
            })
        }
        context = {}

        # Call lambda_handler
        response = lambda_handler(event, context)

        # Asserts
        self.assertEqual(response["statusCode"], 401)
        self.assertIn("error", json.loads(response["body"]))
        self.assertEqual(json.loads(response["body"])["error"], "Invalid token")

    @patch("chat_handler.boto3.client")
    @patch("chat_handler.jwt.decode")
    def test_missing_input_field(self, mock_jwt_decode, mock_bedrock_client):
        # Setup mocks
        mock_bedrock = MagicMock()
        mock_bedrock_client.return_value = mock_bedrock
        mock_jwt_decode.return_value = {
            "email": "john.doe@example.com",
            "sessionId": "mock-session-id",
            "exp": 9999999999
        }

        # Sample event (missing input field)
        event = {
            "httpMethod": "POST",
            "headers": {"Authorization": "Bearer valid-jwt-token"},
            "body": json.dumps({})
        }
        context = {}

        # Call lambda_handler
        response = lambda_handler(event, context)

        # Asserts
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("error", json.loads(response["body"]))
        self.assertEqual(json.loads(response["body"])["error"], "Missing 'input' field")

    @patch("chat_handler.boto3.client")
    @patch("chat_handler.jwt.decode")
    def test_missing_session_id_in_jwt(self, mock_jwt_decode, mock_bedrock_client):
        # Setup mocks
        mock_bedrock = MagicMock()
        mock_bedrock_client.return_value = mock_bedrock
        mock_jwt_decode.return_value = {
            "email": "john.doe@example.com",
            "exp": 9999999999
        }

        # Sample event (missing session ID in JWT)
        event = {
            "httpMethod": "POST",
            "headers": {"Authorization": "Bearer valid-jwt-token"},
            "body": json.dumps({
                "input": "Hello!"
            })
        }
        context = {}

        # Call lambda_handler
        response = lambda_handler(event, context)

        # Asserts
        self.assertEqual(response["statusCode"], 401)
        self.assertIn("error", json.loads(response["body"]))
        self.assertEqual(json.loads(response["body"])["error"], "Missing session ID in token")

    @patch("chat_handler.boto3.client")
    @patch("chat_handler.jwt.decode")
    def test_bedrock_error(self, mock_jwt_decode, mock_bedrock_client):
        # Setup mocks
        mock_bedrock = MagicMock()
        mock_bedrock_client.return_value = mock_bedrock
        mock_bedrock.invoke_agent.side_effect = Exception("Bedrock API error")
        mock_jwt_decode.return_value = {
            "email": "john.doe@example.com",
            "sessionId": "mock-session-id",
            "exp": 9999999999
        }

        # Sample event (Bedrock error)
        event = {
            "httpMethod": "POST",
            "headers": {"Authorization": "Bearer valid-jwt-token"},
            "body": json.dumps({
                "input": "Hello!"
            })
        }
        context = {}

        # Call lambda_handler
        response = lambda_handler(event, context)

        # Asserts
        self.assertEqual(response["statusCode"], 500)
        self.assertIn("error", json.loads(response["body"]))
        self.assertEqual(json.loads(response["body"])["error"], "Internal server error")

if __name__ == "__main__":
    unittest.main()
