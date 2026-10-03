import json
import os
import random
from backend.utils.logger import get_logger

logger = get_logger(__name__)

MESSAGES_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "config", "messages.json"
)


def _load_messages():
    try:
        with open(MESSAGES_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load messages.json: {e}")
        return {}


MESSAGES = _load_messages()


def get_random_message(message_type: str, default_message: str = "Loading...") -> str:
    """
    Get a random message of the specified type from messages.json.
    """
    messages_list = MESSAGES.get(message_type)
    if not messages_list:
        logger.warning(f"Message type '%s' not found in messages.json.", message_type)
        return default_message

    return random.choice(messages_list)


