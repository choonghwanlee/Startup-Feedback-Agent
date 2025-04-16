# logger.py
import logging
import watchtower
import boto3
import time

# Initialize a boto3 session (optional: pass credentials/profile)
session = boto3.Session()

# Define log group and stream
LOG_GROUP = "StartupFeedbackAppLogs"
LOG_STREAM = f"app-{time.strftime('%Y-%m-%d')}"

# Create logger
logger = logging.getLogger("copywriter_logger")
logger.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Console handler (for local dev)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# CloudWatch handler (for AWS logging)
cloudwatch_handler = watchtower.CloudWatchLogHandler(
    log_group_name = LOG_GROUP,
    log_stream_name = LOG_STREAM
)
cloudwatch_handler.setFormatter(formatter)
logger.addHandler(cloudwatch_handler)
