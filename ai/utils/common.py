import uuid
def is_valid_uuid(val: str) -> bool:
    """Check if the provided string is a valid UUID."""
    if not isinstance(val, str):
        return False
    try:
        uuid.UUID(val)
        return True
    except (ValueError, AttributeError, TypeError):
        return False