from __future__ import annotations

import json
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

_DEFAULT_PATH = Path.home() / ".ai-maturity" / "store.db"


class Store:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or _DEFAULT_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._create_tables()

    def _create_tables(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS developers (
                email TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                team TEXT NOT NULL,
                submitted_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL REFERENCES developers(email),
                record_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL REFERENCES developers(email),
                scored_at TEXT NOT NULL,
                scores_json TEXT NOT NULL
            );
        """)

    def save_developer(self, email: str, name: str, team: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            "INSERT OR REPLACE INTO developers (email, name, team, submitted_at) VALUES (?, ?, ?, ?)",
            (email, name, team, now),
        )
        self._conn.commit()

    def get_developer(self, email: str) -> Optional[dict]:
        row = self._conn.execute(
            "SELECT email, name, team, submitted_at FROM developers WHERE email = ?", (email,)
        ).fetchone()
        if row is None:
            return None
        return {"email": row[0], "name": row[1], "team": row[2], "submitted_at": row[3]}

    def save_records(self, email: str, records: List[dict]) -> None:
        self._conn.execute("DELETE FROM records WHERE email = ?", (email,))
        for rec in records:
            self._conn.execute(
                "INSERT INTO records (email, record_json) VALUES (?, ?)",
                (email, json.dumps(rec)),
            )
        self._conn.commit()

    def get_records(self, email: str) -> List[dict]:
        rows = self._conn.execute(
            "SELECT record_json FROM records WHERE email = ?", (email,)
        ).fetchall()
        return [json.loads(row[0]) for row in rows]

    def save_scores(self, email: str, scores: List[dict]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute("DELETE FROM scores WHERE email = ?", (email,))
        self._conn.execute(
            "INSERT INTO scores (email, scored_at, scores_json) VALUES (?, ?, ?)",
            (email, now, json.dumps(scores)),
        )
        self._conn.commit()

    def get_scores(self, email: str) -> List[dict]:
        row = self._conn.execute(
            "SELECT scores_json FROM scores WHERE email = ? ORDER BY scored_at DESC LIMIT 1",
            (email,),
        ).fetchone()
        if row is None:
            return []
        return json.loads(row[0])

    def list_developers(self) -> List[dict]:
        rows = self._conn.execute(
            "SELECT d.email, d.name, d.team, d.submitted_at, "
            "EXISTS(SELECT 1 FROM scores s WHERE s.email = d.email) as has_scores "
            "FROM developers d ORDER BY d.submitted_at DESC"
        ).fetchall()
        return [
            {"email": r[0], "name": r[1], "team": r[2], "submitted_at": r[3], "has_scores": bool(r[4])}
            for r in rows
        ]

    def write_records_jsonl(self, email: str) -> Path:
        records = self.get_records(email)
        tmp = Path(tempfile.mktemp(suffix=".jsonl"))
        with open(tmp, "w") as f:
            for rec in records:
                f.write(json.dumps(rec) + "\n")
        return tmp

    def write_scores_jsonl(self, email: str) -> Path:
        scores = self.get_scores(email)
        tmp = Path(tempfile.mktemp(suffix=".jsonl"))
        with open(tmp, "w") as f:
            for score in scores:
                f.write(json.dumps(score) + "\n")
        return tmp

    def export_developer(self, email: str, output_path: Path) -> int:
        dev = self.get_developer(email)
        if dev is None:
            raise ValueError(f"Developer '{email}' not found")
        records = self.get_records(email)
        with open(output_path, "w", encoding="utf-8") as f:
            meta = {"type": "developer", "email": dev["email"], "name": dev["name"], "team": dev["team"]}
            f.write(json.dumps(meta) + "\n")
            for rec in records:
                f.write(json.dumps(rec) + "\n")
        return len(records)

    def import_developer(self, import_path: Path) -> int:
        with open(import_path, encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]

        if not lines:
            raise ValueError("import file is empty or invalid")

        try:
            meta = json.loads(lines[0])
        except json.JSONDecodeError:
            raise ValueError("import file is invalid — first line must be JSON metadata")

        if meta.get("type") != "developer" or not meta.get("email"):
            raise ValueError("import file is missing developer metadata on line 1")

        records = []
        for line in lines[1:]:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                raise ValueError("import file is invalid — non-JSON line in records")

        self.save_developer(meta["email"], meta["name"], meta["team"])
        self.save_records(meta["email"], records)
        return len(records)

    def reports_dir(self) -> Path:
        d = self.db_path.parent / "reports"
        d.mkdir(parents=True, exist_ok=True)
        return d
