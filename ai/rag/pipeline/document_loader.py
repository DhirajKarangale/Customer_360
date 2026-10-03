from __future__ import annotations
import json
import os
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


class DocumentLoader:

    def __init__(self, data_dir: str) -> None:
        self._data_dir = data_dir

    def discover_documents(self) -> list[str]:
        documents: list[str] = []
        if not os.path.exists(self._data_dir):
            logger.info(f"  [WARN] Data directory not found: {self._data_dir}")
            return documents
        for policy_name in sorted(os.listdir(self._data_dir)):
            policy_dir = os.path.join(self._data_dir, policy_name)
            if not os.path.isdir(policy_dir):
                continue
            for filename in sorted(os.listdir(policy_dir)):
                if not filename.endswith(".json"):
                    continue
                documents.append(os.path.join(policy_name, filename))
        return documents

    def load_document(self, rel_path: str) -> Optional[dict[str, Any]]:
        full_path = os.path.join(self._data_dir, rel_path)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError, OSError) as e:
            logger.info(f"  [WARN] Failed to load {rel_path}: {e}")
            return None
        if not isinstance(data, dict):
            logger.info(f"  [WARN] Invalid document format (not a dict): {rel_path}")
            return None
        content = data.get("content")
        if not content or not isinstance(content, str) or (not content.strip()):
            logger.info(f"  [WARN] Missing or empty content: {rel_path}")
            return None
        metadata = data.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        parts = rel_path.replace("\\", "/").split("/")
        policy_number = parts[0] if len(parts) > 1 else ""
        return {
            "content": content,
            "metadata": metadata,
            "document_path": rel_path,
            "policy_number": policy_number,
        }
