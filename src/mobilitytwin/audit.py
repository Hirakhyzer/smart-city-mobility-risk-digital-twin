"""Hash-chained audit ledger for reproducible mobility simulations."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def append_record(path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Append one hash-chained JSONL audit record."""
    ledger = Path(path)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    previous_hash = _last_hash(ledger)
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "previous_hash": previous_hash,
        "payload": payload,
    }
    record["record_hash"] = _hash_payload(record)
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False, default=str) + "\n")
    return record


def verify_log(path: str | Path) -> dict[str, Any]:
    """Verify that every audit record hash and previous-hash pointer is valid."""
    ledger = Path(path)
    if not ledger.exists():
        return {"valid": True, "records": 0, "last_hash": "GENESIS"}
    previous = "GENESIS"
    count = 0
    with ledger.open("r", encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            stored_hash = record.get("record_hash")
            payload_for_hash = dict(record)
            payload_for_hash.pop("record_hash", None)
            expected_hash = _hash_payload(payload_for_hash)
            if stored_hash != expected_hash or record.get("previous_hash") != previous:
                return {"valid": False, "records": count, "last_hash": previous}
            previous = stored_hash
            count += 1
    return {"valid": True, "records": count, "last_hash": previous}


def _last_hash(path: Path) -> str:
    if not path.exists():
        return "GENESIS"
    last = "GENESIS"
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                last = json.loads(line)["record_hash"]
    return last


def _hash_payload(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()
