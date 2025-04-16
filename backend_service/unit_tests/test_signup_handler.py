import unittest
from unittest.mock import patch, MagicMock
import json
from signup_handler import lambda_handler 
from botocore.exceptions import ClientError


class TestSignupHandler(unittest.TestCase):
    """
    Unit tests for the signup_handler Lambda function.
    Tests cover successful signups, missing input handling,
    and duplicate user detection.
    """

    @patch("signup_handler.boto3.resource")
    @patch("signup_handler.bcrypt.hashpw")
    @patch("signup_handler.jwt.encode")
    def test_successful_signup(self, mock_jwt_encode, mock_bcrypt_hashpw, mock_boto3_resource):
        """
        Test that a user can successfully sign up with valid data.
        Ensures token is returned and item is inserted into DynamoDB.
        """
        # Mock the DynamoDB table and its method
        mock_table = MagicMock()
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb

        mock_table.put_item.return_value = {}  # Simulate successful insert

        # Mock bcrypt and jwt
        mock_bcrypt_hashpw.return_value = b"hashed_password"
        mock_jwt_encode.return_value = "mocked_jwt_token"

        event = {
            "httpMethod": "POST",
            "body": json.dumps({
                "fullname": "John Doe",
                "email": "john.doe@example.com",
                "password": "password123"
            })
        }
        context = {}

        response = lambda_handler(event, context)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertIn("token", body)
        mock_table.put_item.assert_called_once()

    @patch("signup_handler.boto3.resource")
    @patch("signup_handler.bcrypt.hashpw")
    @patch("signup_handler.jwt.encode")
    def test_missing_parameters(self, mock_jwt_encode, mock_bcrypt_hashpw, mock_dynamodb_resource):
        """
        Test that missing required fields (e.g., password) return a 400 error.
        """
        mock_dynamodb = MagicMock()
        mock_dynamodb_resource.return_value = mock_dynamodb
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_bcrypt_hashpw.return_value = "hashed_password"
        mock_jwt_encode.return_value = "mocked_jwt_token"

        event = {
            "httpMethod": "POST",
            "body": json.dumps({
                "email": "john.doe@example.com"
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response["statusCode"], 400)
        self.assertIn("error", json.loads(response["body"]))
        self.assertEqual(json.loads(response["body"])["error"], "Email and password are required")

    @patch("signup_handler.boto3.resource")
    @patch("signup_handler.bcrypt.hashpw")
    @patch("signup_handler.jwt.encode")
    def test_duplicate_user_signup(self, mock_jwt_encode, mock_bcrypt_hashpw, mock_dynamodb_resource):
        """
        Test that a duplicate user signup (same email) returns a 400 error.
        Simulates DynamoDB conditional check failure.
        """
        mock_dynamodb = MagicMock()
        mock_dynamodb_resource.return_value = mock_dynamodb
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table

        mock_bcrypt_hashpw.return_value = b"hashed_password"
        mock_jwt_encode.return_value = "mocked_jwt_token"
        
        # Simulate ConditionalCheckFailedException from DynamoDB
        mock_table.put_item.side_effect = ClientError(
            error_response={"Error": {"Code": "ConditionalCheckFailedException", "Message": "Duplicate"}}, 
            operation_name="PutItem"
        )

        event = {
            "httpMethod": "POST",
            "body": json.dumps({
                "fullname": "John Doe",
                "email": "john.doe@example.com",
                "password": "password123"
            })
        }
        context = {}

        response = lambda_handler(event, context)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertIn("error", body)
        self.assertEqual(body["error"], "User with this email already exists")


if __name__ == "__main__":
    unittest.main()
