import unittest
from unittest.mock import patch, MagicMock
import json
from signup_handler import lambda_handler 
from botocore.exceptions import ClientError


class TestSignupHandler(unittest.TestCase):

    @patch("signup_handler.boto3.resource")
    @patch("signup_handler.bcrypt.hashpw")
    @patch("signup_handler.jwt.encode")
    def test_successful_signup(self, mock_jwt_encode, mock_bcrypt_hashpw, mock_dynamodb_resource):
        # Setup mocks
        mock_dynamodb = MagicMock()
        mock_dynamodb_resource.return_value = mock_dynamodb
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_bcrypt_hashpw.return_value = "hashed_password"
        mock_jwt_encode.return_value = "mocked_jwt_token"

        # Sample event (successful signup)
        event = {
            "httpMethod": "POST",
            "body": json.dumps({
                "fullname": "John Doe",
                "email": "john.doe@example.com",
                "password": "password123"
            })
        }
        context = {}

        # Call lambda_handler
        response = lambda_handler(event, context)

        # Asserts
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("token", json.loads(response["body"]))
        mock_table.put_item.assert_called_once()

    @patch("signup_handler.boto3.resource")
    @patch("signup_handler.bcrypt.hashpw")
    @patch("signup_handler.jwt.encode")
    def test_missing_parameters(self, mock_jwt_encode, mock_bcrypt_hashpw, mock_dynamodb_resource):
        # Setup mocks
        mock_dynamodb = MagicMock()
        mock_dynamodb_resource.return_value = mock_dynamodb
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_bcrypt_hashpw.return_value = "hashed_password"
        mock_jwt_encode.return_value = "mocked_jwt_token"

        # Sample event (missing parameters)
        event = {
            "httpMethod": "POST",
            "body": json.dumps({
                "email": "john.doe@example.com"
            })
        }
        context = {}

        # Call lambda_handler
        response = lambda_handler(event, context)

        # Asserts
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("error", json.loads(response["body"]))
        self.assertEqual(json.loads(response["body"])["error"], "Email and password are required")

    @patch("signup_handler.boto3.resource")
    @patch("signup_handler.bcrypt.hashpw")
    @patch("signup_handler.jwt.encode")
    def test_duplicate_user_signup(self, mock_jwt_encode, mock_bcrypt_hashpw, mock_dynamodb_resource):
        # Setup mocks
        mock_dynamodb = MagicMock()
        mock_dynamodb_resource.return_value = mock_dynamodb
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_bcrypt_hashpw.return_value = "hashed_password"
        mock_jwt_encode.return_value = "mocked_jwt_token"
        
        # Simulate the duplicate email error
        mock_table.put_item.side_effect = ClientError(
            {"Error": {"Code": "ConditionalCheckFailedException"}},
            "PutItem"
        )

        # Sample event (duplicate user)
        event = {
            "httpMethod": "POST",
            "body": json.dumps({
                "fullname": "John Doe",
                "email": "john.doe@example.com",
                "password": "password123"
            })
        }
        context = {}

        # Call lambda_handler
        response = lambda_handler(event, context)

        # Asserts
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("error", json.loads(response["body"]))
        self.assertEqual(json.loads(response["body"])["error"], "User with this email already exists")

if __name__ == "__main__":
    unittest.main()
