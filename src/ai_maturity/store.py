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
                name TEXT PRIMARY KEY,
                team TEXT NOT NULL,
                submitted_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                developer_name TEXT NOT NULL REFERENCES developers(name),
                record_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                developer_name TEXT NOT NULL REFERENCES developers(name),
                scored_at TEXT NOT NULL,
                scores_json TEXT NOT NULL
            );
        """)

    def save_developer(self, name: str, team: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            "INSERT OR REPLACE INTO developers (name, team, submitted_at) VALUES (?, ?, ?)",
            (name, team, now),
        )
        self._conn.commit()

    def get_developer(self, name: str) -> Optional[dict]:
        row = self._conn.execute(
            "SELECT name, team, submitted_at FROM developers WHERE name = ?", (name,)
        ).fetchone()
        if row is None:
            return None
        return {"name": row[0], "team": row[1], "submitted_at": row[2]}

    def save_records(self, developer_name: str, records: List[dict]) -> None:
        self._conn.execute("DELETE FROM records WHERE developer_name = ?", (developer_name,))
        for rec in records:
            self._conn.execute(
                "INSERT INTO records (developer_name, record_json) VALUES (?, ?)",
                (developer_name, json.dumps(rec)),
            )
        self._conn.commit()

    def get_records(self, developer_name: str) -> List[dict]:
        rows = self._conn.execute(
            "SELECT record_json FROM records WHERE developer_name = ?", (developer_name,)
        ).fetchall()
        return [json.loads(row[0]) for row in rows]

    def save_scores(self, developer_name: str, scores: List[dict]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute("DELETE FROM scores WHERE developer_name = ?", (developer_name,))
        self._conn.execute(
            "INSERT INTO scores (developer_name, scored_at, scores_json) VALUES (?, ?, ?)",
            (developer_name, now, json.dumps(scores)),
        )
        self._conn.commit()

    def get_scores(self, developer_name: str) -> List[dict]:
        row = self._conn.execute(
            "SELECT scores_json FROM scores WHERE developer_name = ? ORDER BY scored_at DESC LIMIT 1",
            (developer_name,),
        ).fetchone()
        if row is None:
            return []
        return json.loads(row[0])

    def list_developers(self) -> List[dict]:
        rows = self._conn.execute(
            "SELECT d.name, d.team, d.submitted_at, "
            "EXISTS(SELECT 1 FROM scores s WHERE s.developer_name = d.name) as has_scores "
            "FROM developers d ORDER BY d.submitted_at DESC"
        ).fetchall()
        return [
            {"name": r[0], "team": r[1], "submitted_at": r[2], "has_scores": bool(r[3])}
            for r in rows
        ]

    def write_records_jsonl(self, developer_name: str) -> Path:
        records = self.get_records(developer_name)
        tmp = Path(tempfile.mktemp(suffix=".jsonl"))
        with open(tmp, "w") as f:
            for rec in records:
                f.write(json.dumps(rec) + "\n")
        return tmp

    def write_scores_jsonl(self, developer_name: str) -> Path:
        scores = self.get_scores(developer_name)
        tmp = Path(tempfile.mktemp(suffix=".jsonl"))
        with open(tmp, "w") as f:
            for score in scores:
                f.write(json.dumps(score) + "\n")
        return tmp

    def reports_dir(self) -> Path:
        d = self.db_path.parent / "reports"
        d.mkdir(parents=True, exist_ok=True)
        return d
