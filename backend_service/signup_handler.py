import json
import os
import bcrypt
import jwt
import boto3
from botocore.exceptions import ClientError
import uuid
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
    payload = {
        "email": email,
        "sessionId": str(uuid.uuid4()),
        "exp": datetime.now() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.now(),
        "sub": hashlib.sha256(email.strip().lower().encode('utf-8')).hexdigest()  # Or uuid if preferred
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def lambda_handler(event, context):
    if event["httpMethod"] == "OPTIONS":
        return _response(200, {"message": "Preflight OK"})

    try:
        body = json.loads(event["body"])
        fullname = body.get("fullname")
        email = body.get("email")
        password = body.get("password")

        if not email or not password:
            return _response(400, {"error": "Email and password are required"})

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Generate JWT
        token = generate_jwt(email)

        # Store user in DynamoDB
        user_item = {
            "name": fullname,
            "email": email,
            "password": hashed_password,
            "createdAt": datetime.now().isoformat()
        }
        table.put_item(Item=user_item, ConditionExpression="attribute_not_exists(email)")

        return _response(200, {
            "message": "User created successfully",
            "token": token
        })

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return _response(400, {"error": "User with this email already exists"})
        raise Exception(f"Error creating user: {str(e)}")
    except Exception as e:
        return _response(500, {"error": str(e)})
