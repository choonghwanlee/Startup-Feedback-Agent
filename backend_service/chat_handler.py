import json
import boto3
import os
import jwt
from logger import logger
from dotenv import load_dotenv

load_dotenv()

# === Config ===
JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_ALGORITHM = "HS256"

BEDROCK_AGENT_ID = os.getenv("BEDROCK_AGENT_ID", "your-agent-id")
BEDROCK_AGENT_ALIAS_ID = os.getenv("BEDROCK_AGENT_ALIAS_ID", "your-alias-id")

bedrock_agent = boto3.client("bedrock-agent-runtime")

def verify_jwt(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")


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


def lambda_handler(event, context):
    if event["httpMethod"] == "OPTIONS":
        return _response(200, {"message": "Preflight OK"})
    try:
        headers = event.get("headers", {})
        auth_header = headers.get("authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning(f"Attempt to access protected endpoint with missing JWT Token!!!!")
            return _response(401, {"error": "Missing or invalid Authorization header"})

        token = auth_header.split(" ")[1]
        try:
            payload = verify_jwt(token)
        except Exception as jwt_error:
            logger.warning(f"Attempt to access protected endpoint with invalid JWT Token!!!!")
            return _response(401, {"error": str(jwt_error)})

        user_email = payload["email"]
        session_id = payload.get("sessionId")
        logger.info(f"User {user_email} invoking chat endpoint with session {session_id}")

        if not session_id:
            return _response(401, {"error": "Missing session ID in token"})

        body = json.loads(event.get("body", "{}"))
        user_input = body.get("input")
        end_session = body.get("endSession", False)

        if not user_input:
            return _response(400, {"error": "Missing 'input' field"})

        memory_id = f"memory-{user_email}"

        response = bedrock_agent.invoke_agent(
            agentId=BEDROCK_AGENT_ID,
            agentAliasId=BEDROCK_AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=user_input,
            enableTrace=False,
            endSession=end_session,
            memoryId=memory_id,
        )
        # Collect streaming response chunks
        completion = ""
        for event in response.get("completion", []):
            chunk = event.get('chunk', {})
            completion += chunk.get("bytes", b"").decode()

        refusal_msg = os.environ.get("BEDROCK_REFUSAL_MESSAGE")
        if refusal_msg and completion == refusal_msg:
            logger.warning(f"Guardrail intervened in response generation!!!!")
        
        return _response(200, {"response": completion})
    except Exception as e:
        logger.error(f"Handler error: {str(e)}")
        return _response(500, {"error": "Internal server error", "details": str(e)})
        
