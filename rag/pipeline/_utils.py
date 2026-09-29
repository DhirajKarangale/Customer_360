from __future__ import annotations
import json
import os
from typing import Any

def atomic_write_json(output_path: str, data: Any) -> None:
    tmp_path = output_path + '.tmp'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, output_path)
    except Exception:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        raise

def discover_json_files(directory: str) -> list[str]:
    files: list[str] = []
    if not os.path.exists(directory):
        return files
    for folder_name in sorted(os.listdir(directory)):
        folder_path = os.path.join(directory, folder_name)
        if not os.path.isdir(folder_path):
            continue
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith('.json'):
                files.append(os.path.join(folder_name, filename))
    return files