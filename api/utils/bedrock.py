import base64
import re
from typing import Any, Dict, List, Tuple


def parse_image_data_url(data_url: str) -> Tuple[str, bytes]:
    """
    Parse a data URL in the format 'data:image/png;base64,<data>'
    Returns (format, decoded_bytes)
    """
    if not data_url.startswith("data:image/"):
        raise ValueError("Invalid image data URL format")

    # Extract mime type and base64 data
    # Format: data:image/png;base64,iVBORw0KGgoAAAANS...
    match = re.match(r"data:image/(\w+);base64,(.+)", data_url)
    if not match:
        raise ValueError("Invalid image data URL format")

    image_format = match.group(1).lower()
    base64_data = match.group(2)

    # Decode base64
    image_bytes = base64.b64decode(base64_data)

    return image_format, image_bytes


def convert_messages_to_bedrock(messages: List[Dict[str, Any]]) -> Tuple[List[Dict[str, str]], List[Dict[str, Any]]]:
    """
    Convert OpenAI-format messages to AWS Bedrock Converse API format.
    
    Returns:
        (system_messages, bedrock_messages)
        - system_messages: List of system message dicts, each with 'text' key containing a string
                          Example: [{'text': 'You are helpful'}, {'text': 'Be concise'}]
        - bedrock_messages: List of user/assistant message dicts with 'role' and 'content' keys
                          Example: [{'role': 'user', 'content': [{'text': 'Hello'}, {'image': {...}}]}]
    """
    system_messages = []
    bedrock_messages = []

    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")

        # Extract system messages separately
        if role == "system":
            if isinstance(content, str):
                system_messages.append({"text": content})
            elif isinstance(content, list):
                for part in content:
                    if part.get("type") == "text":
                        system_messages.append({"text": part.get("text", "")})
            continue

        # Convert user/assistant messages
        if role not in ["user", "assistant"]:
            continue

        content_blocks = []

        if isinstance(content, str):
            content_blocks.append({"text": content})
        elif isinstance(content, list):
            for part in content:
                part_type = part.get("type")

                if part_type == "text":
                    text_content = part.get("text", "")
                    if text_content:
                        content_blocks.append({"text": text_content})

                elif part_type == "image_url":
                    image_url = part.get("image_url", {}).get("url", "")
                    if image_url.startswith("data:image/"):
                        try:
                            image_format, image_bytes = parse_image_data_url(image_url)
                            content_blocks.append({
                                "image": {
                                    "format": image_format,
                                    "source": {"bytes": image_bytes}
                                }
                            })
                        except Exception as e:
                            print(f"Error parsing image data URL: {e}")

        if content_blocks:
            bedrock_messages.append({
                "role": role,
                "content": content_blocks
            })

    return system_messages, bedrock_messages
