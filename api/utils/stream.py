import json
import time
import traceback
import uuid
from typing import Any, Dict, Optional


def format_sse(payload: dict) -> str:
    """Format a payload as a Server-Sent Event."""
    return f"data: {json.dumps(payload, separators=(',', ':'))}\n\n"


def stream_bedrock(
    stream,
    endpoint_name: Optional[str] = None,
    start_time: Optional[float] = None,
):
    """
    Yield Server-Sent Events for AWS Bedrock converse_stream response.
    
    Bedrock stream events:
    - messageStart
    - contentBlockStart
    - contentBlockDelta (with delta.text)
    - contentBlockStop
    - messageStop
    - metadata
    """
    try:
        if start_time is None:
            start_time = time.time()
        first_chunk_logged = False

        message_id = f"msg-{uuid.uuid4().hex}"
        text_stream_id = "text-1"
        text_started = False
        text_finished = False
        finish_reason = None
        usage_data = None

        yield format_sse({"type": "start", "messageId": message_id})

        for event in stream:
            if not first_chunk_logged:
                first_chunk_logged = True
                print(
                    f"[{endpoint_name or 'bedrock-stream'}] Time to first chunk: {(time.time() - start_time) * 1000:.2f}ms"
                )

            # Handle different event types from Bedrock
            if "contentBlockDelta" in event:
                delta = event["contentBlockDelta"]["delta"]
                if "text" in delta:
                    if not text_started:
                        yield format_sse({"type": "text-start", "id": text_stream_id})
                        text_started = True
                    yield format_sse(
                        {
                            "type": "text-delta",
                            "id": text_stream_id,
                            "delta": delta["text"],
                        }
                    )

            elif "messageStop" in event:
                stop_reason = event["messageStop"].get("stopReason")
                if stop_reason:
                    # Map Bedrock stop reasons to our format
                    # Bedrock: end_turn, max_tokens, stop_sequence, tool_use, content_filtered
                    if stop_reason == "end_turn":
                        finish_reason = "stop"
                    elif stop_reason == "max_tokens":
                        finish_reason = "length"
                    else:
                        finish_reason = stop_reason

            elif "metadata" in event:
                metadata = event["metadata"]
                if "usage" in metadata:
                    bedrock_usage = metadata["usage"]
                    usage_data = {
                        "inputTokens": bedrock_usage.get("inputTokens", 0),
                        "outputTokens": bedrock_usage.get("outputTokens", 0),
                        "totalTokens": bedrock_usage.get("totalTokens", 0),
                    }

        if text_started and not text_finished:
            yield format_sse({"type": "text-end", "id": text_stream_id})
            text_finished = True

        finish_metadata: Dict[str, Any] = {}
        if finish_reason is not None:
            finish_metadata["finishReason"] = finish_reason

        if usage_data is not None:
            usage_payload = {
                "promptTokens": usage_data["inputTokens"],
                "completionTokens": usage_data["outputTokens"],
                "totalTokens": usage_data["totalTokens"],
            }
            finish_metadata["usage"] = usage_payload

        if finish_metadata:
            yield format_sse({"type": "finish", "messageMetadata": finish_metadata})
        else:
            yield format_sse({"type": "finish"})

        print(
            f"[{endpoint_name or 'bedrock-stream'}] Total stream time: {(time.time() - start_time) * 1000:.2f}ms"
        )

        yield "data: [DONE]\n\n"
    except Exception:
        traceback.print_exc()
        raise
