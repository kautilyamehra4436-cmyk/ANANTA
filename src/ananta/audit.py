"""SQLite-backed append-only audit ledger with a SHA-256 hash chain."""
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4


class AuditLedger:
    def __init__(self, path: str):
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL UNIQUE,
                timestamp TEXT NOT NULL,
                event TEXT NOT NULL,
                details_json TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                event_hash TEXT NOT NULL UNIQUE
            )
        """)
        self.connection.commit()

    @staticmethod
    def _hash(event_id, timestamp, event, details_json, previous_hash):
        material = "\n".join((event_id, timestamp, event, details_json, previous_hash))
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    def append(self, event: str, details: dict) -> dict:
        row = self.connection.execute(
            "SELECT event_hash FROM audit_events ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        previous_hash = row[0] if row else "GENESIS"
        event_id = str(uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        details_json = json.dumps(details, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        event_hash = self._hash(event_id, timestamp, event, details_json, previous_hash)
        with self.connection:
            self.connection.execute(
                "INSERT INTO audit_events(event_id,timestamp,event,details_json,previous_hash,event_hash) VALUES(?,?,?,?,?,?)",
                (event_id, timestamp, event, details_json, previous_hash, event_hash),
            )
        return {"event": event, "details": json.loads(details_json), "event_id": event_id,
                "timestamp": timestamp, "previous_hash": previous_hash, "event_hash": event_hash}

    def read_all(self) -> list[dict]:
        rows = self.connection.execute(
            "SELECT event_id,timestamp,event,details_json,previous_hash,event_hash FROM audit_events ORDER BY sequence"
        ).fetchall()
        return [{"event_id": r[0], "timestamp": r[1], "event": r[2],
                 "details": json.loads(r[3]), "previous_hash": r[4], "event_hash": r[5]} for r in rows]

    def verify(self) -> dict:
        previous = "GENESIS"
        count = 0
        for row in self.connection.execute(
            "SELECT event_id,timestamp,event,details_json,previous_hash,event_hash FROM audit_events ORDER BY sequence"
        ):
            event_id, timestamp, event, details_json, prev_hash, digest = row
            expected = self._hash(event_id, timestamp, event, details_json, prev_hash)
            if prev_hash != previous or digest != expected:
                return {"verified": False, "events": count, "failed_event_id": event_id}
            previous = digest
            count += 1
        return {"verified": True, "events": count, "head_hash": previous}

    def close(self):
        self.connection.close()
