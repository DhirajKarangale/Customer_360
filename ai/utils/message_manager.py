import os
import json
import random
import logging

logger = logging.getLogger(__name__)

_MESSAGES = None
_MESSAGES_FILE = os.path.join(os.path.dirname(__file__), "messages.json")

def _load_messages():
    global _MESSAGES
    if _MESSAGES is None:
        try:
            with open(_MESSAGES_FILE, "r", encoding="utf-8") as f:
                _MESSAGES = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load messages.json: {e}")
            _MESSAGES = {}

def get_message(message_type: str, default: str = "", **kwargs) -> str:
    """
    Returns a random message from the messages.json file for the given type.
    Formats the string with kwargs if provided.
    """
    _load_messages()
    options = _MESSAGES.get(message_type, [])
    if not options:
        msg = default
    else:
        msg = random.choice(options)
    
    if kwargs:
        try:
            return msg.format(**kwargs)
        except Exception as e:
            logger.error(f"Message formatting failed: {e}")
            return msg
    return msg
