import json
from typing import Any


def ensure_md_string(value: Any) -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return ''
    return '```text\n' + json.dumps(value, indent=2, ensure_ascii=False) + '\n```'
