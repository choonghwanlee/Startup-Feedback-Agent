import unittest
from unittest.mock import patch, MagicMock
import json
from login_handler import lambda_handler  # Replace with the correct import path

class TestLoginHandler(unittest.TestCase):

    @patch("login_handler.boto3.resource")
    @patch("login_handler.bcrypt.checkpw")
    @patch("login_handler.jwt.encode")
    def test_successful_login(self, mock_jwt_encode, mock_bcrypt_checkpw, mock_dynamodb_resource):
        # Setup mocks
        mock_dynamodb = MagicMock()
        mock_dynamodb_resource.return_value = mock_dynamodb
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_bcrypt_checkpw.return_value = True
        mock_jwt_encode.return_value = "mocked_jwt_token"

        # Simulating a DynamoDB response with a valid user
        mock_table.get_item.return_value = {
            "Item": {
                "email": "john.doe@example.com",
                "password": "hashed_password"
            }
        }

        # Sample event (successful login)
        event = {
            "httpMethod": "POST",
            "body": json.dumps({
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
        mock_table.get_item.assert_called_once()

    @patch("login_handler.boto3.resource")
    @patch("login_handler.bcrypt.checkpw")
    @patch("login_handler.jwt.encode")
    def test_invalid_email(self, mock_jwt_encode, mock_bcrypt_checkpw, mock_dynamodb_resource):
        # Setup mocks
        mock_dynamodb = MagicMock()
        mock_dynamodb_resource.return_value = mock_dynamodb
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_bcrypt_checkpw.return_value = False
        mock_jwt_encode.return_value = "mocked_jwt_token"

        # Simulating a DynamoDB response with no user found
        mock_table.get_item.return_value = {}

        # Sample event (invalid email)
        event = {
            "httpMethod": "POST",
            "body": json.dumps({
                "email": "john.doe@example.com",
                "password": "password123"
            })
        }
        context = {}

        # Call lambda_handler
        response = lambda_handler(event, context)

        # Asserts
        self.assertEqual(response["statusCode"], 401)
        self.assertIn("error", json.loads(response["body"]))
        self.assertEqual(json.loads(response["body"])["error"], "Invalid email or password")

    @patch("login_handler.boto3.resource")
    @patch("login_handler.bcrypt.checkpw")
    @patch("login_handler.jwt.encode")
    def test_invalid_password(self, mock_jwt_encode, mock_bcrypt_checkpw, mock_dynamodb_resource):
        # Setup mocks
        mock_dynamodb = MagicMock()
        mock_dynamodb_resource.return_value = mock_dynamodb
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_bcrypt_checkpw.return_value = False
        mock_jwt_encode.return_value = "mocked_jwt_token"

        # Simulating a DynamoDB response with a valid user but incorrect password
        mock_table.get_item.return_value = {
            "Item": {
                "email": "john.doe@example.com",
                "password": "hashed_password"
            }
        }

        # Sample event (invalid password)
        event = {
            "httpMethod": "POST",
            "body": json.dumps({
                "email": "john.doe@example.com",
                "password": "wrongpassword"
            })
        }
        context = {}

        # Call lambda_handler
        response = lambda_handler(event, context)

        # Asserts
        self.assertEqual(response["statusCode"], 401)
        self.assertIn("error", json.loads(response["body"]))
        self.assertEqual(json.loads(response["body"])["error"], "Invalid email or password")

if __name__ == "__main__":
    unittest.main()
