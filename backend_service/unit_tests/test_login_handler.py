import unittest
from unittest.mock import patch, MagicMock
import json
from login_handler import lambda_handler  # Replace with the correct import path

class TestLoginHandler(unittest.TestCase):
    """
    Unit test suite for the login_handler Lambda function.

    This suite tests various login scenarios such as:
    - Successful login with valid email and password
    - Invalid login due to incorrect email
    - Invalid login due to incorrect password

    External dependencies like DynamoDB, bcrypt, and JWT are mocked to isolate logic.
    """

    @patch("login_handler.table")
    @patch("login_handler.bcrypt.checkpw")
    @patch("login_handler.jwt.encode")
    def test_successful_login(self, mock_jwt_encode, mock_bcrypt_checkpw, mock_table):
        """
        Test a successful login when the user provides correct email and password.

        Mocks:
        - DynamoDB `get_item` returns a valid user record
        - bcrypt password check returns True
        - JWT token generation

        Verifies:
        - Status code is 200
        - A JWT token is included in the response
        """
        # Configure the DynamoDB table mock to return a valid user
        mock_table.get_item.return_value = {
            "Item": {
                "email": "john.doe@example.com",
                "password": "hashed_password"
            }
        }
        # Simulate correct password check:
        mock_bcrypt_checkpw.return_value = True
        # Simulate JWT generation:
        mock_jwt_encode.return_value = "mocked_jwt_token"

        # Create a sample login event:
        event = {
            "httpMethod": "POST",
            "body": json.dumps({
                "email": "john.doe@example.com",
                "password": "password123"
            })
        }
        context = {}

        response = lambda_handler(event, context)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertIn("token", body)
        self.assertEqual(body["token"], "mocked_jwt_token")


    @patch("login_handler.boto3.resource")
    @patch("login_handler.bcrypt.checkpw")
    @patch("login_handler.jwt.encode")
    def test_invalid_email(self, mock_jwt_encode, mock_bcrypt_checkpw, mock_dynamodb_resource):
        """
        Test login attempt with an invalid email.

        Mocks:
        - Simulates a response where no user is found in DynamoDB for the provided email

        Verifies:
        - Status code is 401
        - Error message indicates invalid email or password
        """
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
        """
        Test login attempt with an incorrect password.

        Mocks:
        - Simulates a response with a valid user but incorrect password check

        Verifies:
        - Status code is 401
        - Error message indicates invalid email or password
        """
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
