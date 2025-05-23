import json
import os
import bcrypt
import jwt
import boto3
import uuid
from logger import logger
from datetime import datetime, timedelta
from dotenv import load_dotenv
import hashlib

load_dotenv()

# === Config ===
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRATION_HOURS = 24

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(DYNAMODB_TABLE)


def _response(status_code, body):
    """
    Constructs a standardized HTTP response.

    Args:
        status_code (int): The HTTP status code.
        body (dict): The response body to be JSON-encoded.

    Returns:
        dict: A properly formatted HTTP response with CORS headers.
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "OPTIONS,POST",
        },
        "body": json.dumps(body)
    }


def generate_jwt(email):
    """
    Generates a JSON Web Token for a given email.

    Args:
        email (str): The email address to encode into the JWT.

    Returns:
        str: A signed JWT string.
    """
    payload = {
        "email": email,
        "sessionId": str(uuid.uuid4()),
        "exp": datetime.now() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.now(),
        "sub": hashlib.sha256(email.strip().lower().encode('utf-8')).hexdigest()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def lambda_handler(event, context):
    """
    AWS Lambda handler for user login.

    Handles CORS preflight requests and user login by validating email and password
    against records in DynamoDB. Returns a JWT on successful login.

    Args:
        event (dict): The Lambda event payload.
        context (object): The Lambda context object.

    Returns:
        dict: API Gateway-compatible HTTP response.
    """
    if event["httpMethod"] == "OPTIONS":
        return _response(200, {"message": "Preflight OK"})

    try:
        body = json.loads(event["body"])
        email = body.get("email")
        password = body.get("password")

        if not email or not password:
            return _response(400, {"error": "Email and password are required"})

        logger.info(f"User {email} invoking attemping to login...")

        # Look up user in DynamoDB
        result = table.get_item(Key={"email": email})
        user = result.get("Item")

        if not user:
            logger.warning("Invalid user email provided!!!!")
            return _response(401, {"error": "Invalid email or password"})

        hashed_password = user["password"]

        if not bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
            logger.warning("Invalid password provided!!!!")
            return _response(401, {"error": "Invalid email or password"})

        # Generate JWT
        token = generate_jwt(email)

        return _response(200, {
            "message": "Login successful",
            "token": token
        })

    except Exception as e:
        return _response(500, {"error": str(e)})
