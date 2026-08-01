from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .decoder_packet import DecoderPacket


class PacketValidationError(ValueError):
    pass


def extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
        if text.lower().startswith("json"):
            text = text[4:].lstrip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise PacketValidationError(f"Decoder output is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise PacketValidationError("Decoder output must be one JSON object")
    return data


def load_packet(path: Path | str) -> DecoderPacket:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return DecoderPacket.from_dict(data)


def validate_text(text: str) -> DecoderPacket:
    return DecoderPacket.from_dict(extract_json_object(text))
