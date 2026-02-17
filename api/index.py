from typing import Any, List
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, Request as FastAPIRequest
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import boto3

from .utils.stream import stream_bedrock
from .utils.bedrock import convert_messages_to_bedrock

load_dotenv(".env.local")

# Initialize Bedrock client
bedrock_runtime = boto3.client(
    "bedrock-runtime",
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

is_production = (
    os.getenv("RAILWAY_ENVIRONMENT_NAME") == "production"
    or os.getenv("VERCEL_ENV") == "production"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://screen.vision", "https://www.screen.vision"]
    if is_production
    else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessagesRequest(BaseModel):
    messages: List[Any]


@app.post("/api/step")
@limiter.limit("20/minute;300/hour")
async def handle_step_chat(request: FastAPIRequest, body: MessagesRequest):
    """
    Generate step-by-step instructions using Claude Sonnet 4.
    """
    system_messages, bedrock_messages = convert_messages_to_bedrock(body.messages)

    # Use Claude Sonnet 4 for step planning
    model_id = "us.anthropic.claude-sonnet-4-20250514-v1:0"

    inference_config = {
        "maxTokens": 4096,
        "temperature": 1.0,
    }

    stream = bedrock_runtime.converse_stream(
        modelId=model_id,
        messages=bedrock_messages,
        system=system_messages or None,
        inferenceConfig=inference_config,
    )

    response = StreamingResponse(
        stream_bedrock(stream["stream"], endpoint_name="step"),
        media_type="text/event-stream",
    )

    return response


@app.post("/api/help")
@limiter.limit("8/minute;100/hour")
async def handle_help_chat(request: FastAPIRequest, body: MessagesRequest):
    """
    Answer help questions using Claude Sonnet 4.
    """
    system_messages, bedrock_messages = convert_messages_to_bedrock(body.messages)

    # Use Claude Sonnet 4 for help
    model_id = "us.anthropic.claude-sonnet-4-20250514-v1:0"

    inference_config = {
        "maxTokens": 4096,
        "temperature": 1.0,
    }

    stream = bedrock_runtime.converse_stream(
        modelId=model_id,
        messages=bedrock_messages,
        system=system_messages or None,
        inferenceConfig=inference_config,
    )

    response = StreamingResponse(
        stream_bedrock(stream["stream"], endpoint_name="help"),
        media_type="text/event-stream",
    )

    return response


@app.post("/api/check")
@limiter.limit("30/minute;500/hour")
async def handle_check_chat(request: FastAPIRequest, body: MessagesRequest):
    """
    Check step completion using Claude 3.5 Haiku (fast and cheap).
    """
    system_messages, bedrock_messages = convert_messages_to_bedrock(body.messages)

    # Use Claude 3.5 Haiku for fast verification
    model_id = "us.anthropic.claude-3-5-haiku-20241022-v1:0"

    inference_config = {
        "maxTokens": 1024,
        "temperature": 0.5,
    }

    stream = bedrock_runtime.converse_stream(
        modelId=model_id,
        messages=bedrock_messages,
        system=system_messages or None,
        inferenceConfig=inference_config,
    )

    response = StreamingResponse(
        stream_bedrock(stream["stream"], endpoint_name="check"),
        media_type="text/event-stream",
    )

    return response


@app.post("/api/coordinates")
@limiter.limit("15/minute;200/hour")
async def handle_coordinate_chat(request: FastAPIRequest, body: MessagesRequest):
    """
    Generate coordinates using Claude Sonnet 4 (strong vision capabilities).
    """
    system_messages, bedrock_messages = convert_messages_to_bedrock(body.messages)

    # Use Claude Sonnet 4 for coordinate detection (vision)
    model_id = "us.anthropic.claude-sonnet-4-20250514-v1:0"

    inference_config = {
        "maxTokens": 1024,
        "temperature": 0.5,
    }

    stream = bedrock_runtime.converse_stream(
        modelId=model_id,
        messages=bedrock_messages,
        system=system_messages or None,
        inferenceConfig=inference_config,
    )

    response = StreamingResponse(
        stream_bedrock(stream["stream"], endpoint_name="coordinates"),
        media_type="text/event-stream",
    )

    return response
