from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import best_match

_SCHEMA_DIR = Path(__file__).resolve().parent

_FORMAT_CHECKER = Draft202012Validator.FORMAT_CHECKER


@lru_cache(maxsize=32)
def _validator_for_resolved_path(resolved_schema_path: str) -> Draft202012Validator:
    with open(resolved_schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    return Draft202012Validator(schema, format_checker=_FORMAT_CHECKER)


def _resolve_schema_path(schema_file: str | Path) -> Path:
    path = Path(schema_file)
    if not path.is_absolute():
        path = _SCHEMA_DIR / path
    return path.resolve()


def validate_payload(instance: Any, schema_file: str | Path) -> None:
    resolved = _resolve_schema_path(schema_file)
    if not resolved.is_file():
        raise FileNotFoundError(f"JSON Schema not found: {resolved}")
    validator = _validator_for_resolved_path(str(resolved))
    error = best_match(validator.iter_errors(instance))
    if error is not None:
        raise ValueError(error.message) from error
