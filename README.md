# Startup-Feedback-Agent

A web search agent that can help you do market research for your startup idea

## Incorporation of each week's elements:

1. AWS Bedrock with long-term memory (week 1)
2. Enterprise-grade AI solution with user authentication and secure chat interface using AWS DynamoDB to store and authenticate users (week 3).
3. Text generation service, with security measures implemented via JWT to gate endpoints (week 5)
4. Scalable, production-ready AI services using AWS Lambda and AWS API Gateway (week 6)
5. Deployed full-stack application with NextJS (week 9)
6. Implemented privacy & security measures using AWS Bedrock Guardrails, with AWS CloudWatch for auditing (week 10)

## Technical Implementation

### Architecture Design

1.  Users sign-up with name, email, and password, which is sent to our `/users/signup` endpoint. This information is stored in DynamoDB with the password hashed using `bcrypt`. We also prevent duplicate accounts by comparing the sign-up email with the emails in our DynamoDB table. The `/users/signup` endpoint will then generate a JWT token and return that as the response to the user.
2.  Users login with email and password, which is sent to our `/users/login` endpoint. We query DynamoDB to check a. if the user exists and b. if the password entered matches the decrypted password from the DynamoDB. If both are true, we generate a JWT token and return that as the response to the user.
3.  Once users sign-up or log-in, they are navigated to a chat UI. They can then ask a question to the agent, which triggers the `/chat` endpoint. The JWT token they received upon log-in or sign-up is set as the Authorization header in the POST request.
4.  The `/chat` endpoint first checks that the JWT token is valid by decrypting it and checking if a valid payload exists using `verify_jwt()`
5.  If we have a valid JWT token, then AWS Bedrock Guardrail first classifies the prompt as harmful or not (based on criterias I will outline later), and will refuse to answer if the prompt is flagged.
6.  Finally, our agent will process the user's question, generate a response, and return it to the user in the front-end. The agent also uses long-term memory to retain any important information across chat sessions. This allows the agent to remember what the user's startup idea and details are.
7.  If AWS CloudWatch Logger raises a lot of warnings in a short time frame, we use CloudWatch Alerts to send an email to an admin (me in this case) for oversight.

### Code Testing & Quality

We use `unittests` and `coverage` to assess the quality of our code. For each of our lambda functions, we mock various scenarios (see below):

| File Name        | Test Case Description                                   | Status Code | Notes                                            |
| ---------------- | ------------------------------------------------------- | ----------- | ------------------------------------------------ |
| `signup_handler` | Successful signup with valid input                      | 200         | Mocks DynamoDB `put_item`                        |
|                  | Missing required fields (email or password)             | 400         | Validates input fields                           |
|                  | Email already exists (DynamoDB conditional check fails) | 400         | Simulates `ConditionalCheckFailedException`      |
|                  | Internal server error during signup                     | 500         | Simulates unexpected error                       |
| `login_handler`  | Successful login with valid credentials                 | 200         | Mocks `get_item`, `bcrypt.checkpw`, `jwt.encode` |
|                  | Missing email or password in input                      | 400         | Validates input fields                           |
|                  | Email not found in database                             | 401         | Simulates nonexistent user                       |
|                  | Incorrect password                                      | 401         | Mocks incorrect `bcrypt.checkpw`                 |
|                  | Internal server error during login                      | 500         | Simulates unexpected error                       |
| `chat_handler`   | Successful chat with valid JWT and input                | 200         | Mocks `invoke_agent` and response chunks         |
|                  | Missing or invalid JWT token                            | 401         | Simulates JWT decoding failure                   |
|                  | Missing `input` field in request body                   | 400         | Validates user input                             |
|                  | Missing `sessionId` in JWT payload                      | 401         | Ensures session ID is required                   |
|                  | Bedrock agent invocation error                          | 500         | Simulates Bedrock API failure                    |

We can run the tests using:

```bash
coverage run -m unittest discover
coverage report
```

Below are the results

We also add docstrings for each function for better code quality and readability.

### Performance and Scalability

We ensure good performance and scalability by using AWS API Gateway. This helps with:

1. Auto-Scaling: Automatically handles sudden spikes in traffic—no need to manage infrastructure.
2. Integration with Lambdas: Each API call can trigger a separate Lambda function execution that scales independently.
3. Request Throttling: Helps control traffic to backend services, preventing overload and ensuring stable response times under heavy usage.

### Error Handling & Resilience

Frequent try & except blocks and verbose error messages allow us to build resilient endpoints with high fault tolerance.

## Documentation

### API Documentation

#### 1. User Signup

**Endpoint:**
`POST /users/signup`

**Description:**
Creates a new user account by accepting user credentials and storing them in DynamoDB.

**Request Headers:**

- `Content-Type: application/json`

**Request Body**

```json
{
  "fullname": "John Doe",
  "email": "user@example.com",
  "password": "yourPassword123"
}
```

**Responses**

- **`200 OK`**

```json
{
  "message": "User created successfully",
  "token": "<JWT_TOKEN>"
}
```

- **`400 Bad Request`**

```json
{
  "error": "Email and password are required"
}
```

- **`409 Conflict`**

```json
{
  "error": "User already exists"
}
```

#### 2. User Login

**Endpoint:**
`POST /users/login`

**Description:**
Authenticates the user and returns a JWT token.

**Request Headers:**

- `Content-Type: application/json`

**Request Body**

```json
{
  "email": "user@example.com",
  "password": "yourPassword123"
}
```

**Responses**

- **`200 OK`**

```json
{
  "token": "<JWT_TOKEN>"
}
```

- **`400 Bad Request`**

```json
{
  "error": "Missing email or password"
}
```

- **`401 Unathorized`**

```json
{
  "error": "Invalid email or password"
}
```

#### 3. Chat with Agent

**Endpoint:**
`POST /chat`

**Description:**
Sends a message to the Bedrock agent and returns the agent's response.

**Request Headers:**

- `Content-Type: application/json`
- `Authorization: Bearer <JWT_TOKEN>`

**Request Body**

```json
{
  "input": "Give me a market size evaluation for my startup idea"
}
```

**Responses**

- **`200 OK`**

```json
{
  "response": "Assuming that there are 20,000 dog owners in California..."
}
```

- **`400 Bad Request`**

```json
{
  "error": "Missing 'input' field"
}
```

- **`401 Unauthorized`**

```json
{
  "error": "Missing or invalid Authorization header"
}
```

### Deployment guide

To deploy your AWS Lambda functions and connect them to AWS API Gateway, you can follow the instructions here:

#### **1. Create a zip file of repository content**

First, run the following command:

```bash
pip3 install -t dependencies -r requirements.txt --platform manylinux2014_x86_64 --python-version 3.12 --only-binary=:all:
```

This creates a new folder called `dependencies` with all the dependencies installed. We specify platform to x86_64 to ensure it is consistent with AWS Lambda architecture.

```bash
(cd dependencies; zip ../aws_lambda_artifact.zip -r .)
```

This will zip the dependencies into a zip file called `aws_lambda_artifact.zip`. To this, we add our python files with the following comands:

`zip aws_lambda_artifact.zip -u NAME_OF_FILE.py`, where `NAME_OF_FILE` refers to a .py file in our directory.

#### **2. Create a new AWS Lambda Function**

In the AWS Lambda console, create a new function. Change the runtime to your Python runtime (in my case, it was Python 3.12), and under Additional Configurations, 'Enable Function URL' then set Auth type to NONE.

After pressing 'Create function', a new AWS Lambda function will be created.

Change the handler from the default value to <your_file_name>.lambda_handler, specifying the filename of our Lambda function and the name of our main handler function.

#### **3. Upload zip file to AWS Lambda Function**

Finally, under 'Code Source', select upload from .zip file and upload the aws_lambda_artifact.zip you created in Step 1. This will load our repository into AWS Lambda

Finally, in the 'ENVIRONMENT VARIABLES' section of the built-in IDE, add the following keys:

```makefile
DYNAMODB_TABLE =
JWT_SECRET=
JWT_ALGORITHM =
BEDROCK_AGENT_ID =
BEDROCK_AGENT_ALIAS_ID =
BEDROCK_REFUSAL_MESSAGE =
```

#### **4. Deploy with API Gateway**

After each of the Lambda functions are deployed, you can deploy them with AWS API Gateway by doing the following:

1. Create a HTTP API endpoint
2. Integrate with AWS Lambda, defining three routes for each of the three functions
3. Create the API Gateway
4. Navigate to CORS on the sidebar, and

   - enable your frontend URL under `Access-Control-Allow-Origin`
   - headers `content-type` and `authorization` under `Access-Control-Allow-Headers`
   - methods `POST` and `OPTIONS` under `Access-Control-Allow-Methods`

5. Toggle `Access-Control-Allow-Credentials` to yes.

### User Manual

Once you enter the app via the [landing page](), you can navigate to login/signup via the buttons on the top right corner of the screen. Create a new account if you don't have an account, or log in with your previous credentials.

Then, you will be navigated to a chat interface where you can ask questions about your startup. At first, specify clearly what your idea is, and state a question you want answered. The chatbot might ask you clarifying questions for more clarity. The more questions you answer, the more fine-grained the chatbot responses will be. But it's not strictly mandatory for you to answer the chatbot's clarifying questions: you can just tell it to make assumptions wherever you want it to.

You can logout of the session by pressing `logout` on the top right. When you login next time, the agent should remember key details from your previous interactions.

## Security & Responsibility

### AWS Bedrock Guardrails

We configure Guardrails with our Bedrock Agents. Below are the criterions that the Guardrails flags/redacts:

| Type                           | Category           | Subcategory / Detail                                                                                                                               |
| ------------------------------ | ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Hate                           | Harmful Categories |                                                                                                                                                    |
| Insults                        | Harmful Categories |                                                                                                                                                    |
| Sexual Content                 | Harmful Categories |                                                                                                                                                    |
| Violence                       | Harmful Categories |                                                                                                                                                    |
| Misconduct                     | Harmful Categories |                                                                                                                                                    |
| Unregulated Health and Finance | Denied Topics      | Content offering medical, health, or financial advice without credentials or regulatory oversight, including unverified treatments or investments. |
| Scams and Exploitation         | Denied Topics      | Content that promotes deceptive, manipulative, or fraudulent business practices, including scams, data harvesting, or financial exploitation.      |
| Legal Advice                   | Denied Topics      | Content that provides legal guidance, contract interpretation, or regulatory compliance recommendations without a licensed legal professional.     |
| Dangerous or Illegal Ideas     | Denied Topics      | Content that promotes, enables, or suggests physical harm, violence, weapons, terrorism, or self-harm against individuals or groups.               |

The denied topics include user input (specifically startup ideas) that we think are unethical or possess great legal liability. For example, we don't want our assistant to give legal advice or encourage development of unregulated health or financial services.

In addition, we redact PII in output to prevent Protected Attribute Inference attacks. For example, we redact user information like name, phone, email, etc. when the agent is prompted to generate it.

Finally, we detect and flag prompt attacks, which include SQL injections, jailbreak prompts, etc. This further boosts the security of our application.

### JWT Tokens

As mentioned earlier, we issue JWT tokens to authenticated users, which allows users to access gated endpoints like `/chat`. This prevents malicious, unathorized acters from accessing our text generation endpoints – which can lead to severe security risks.

In the future, using API Gateway to enable rate limiting will further prevent malicious actors from exploiting our APIs.

### Compliance

_Note: we leverage the same compliance documentaiton as Week 10_

Our startup feedback assistant is designed with compliance in mind, particularly with respect to key data protection regulations such as the General Data Protection Regulation (GDPR). We ensure that no personally identifiable information (PII) is stored or exposed during the generation process. All interactions with the model are stateless and ephemeral—PII is masked before being sent to the Bedrock model, and we do not log any raw input or output that contains user-submitted data unless it has been fully redacted.

In addition to privacy regulations, our app aligns with the NIST AI Risk Management Framework (AI RMF) to ensure responsible AI use. This includes proactively managing risks related to safety, fairness, transparency, and accountability. Through the use of Amazon Bedrock Guardrails, we block harmful or inappropriate content as well as any prompt attack methods. We also maintain audit logs, human oversight in critical workflows, and mechanisms for flagging and reviewing questionable prompts. These practices support a trustworthy AI system that is not only technically secure but also aligned with emerging ethical standards.
