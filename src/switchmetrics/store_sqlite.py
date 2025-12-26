from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime, timezone

from .parse_ios_show_int import InterfaceCounters


SCHEMA = """
CREATE TABLE IF NOT EXISTS interface_samples (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts_utc TEXT NOT NULL,
  device TEXT NOT NULL,
  iface TEXT NOT NULL,

  input_pkts INTEGER NOT NULL,
  input_bytes INTEGER NOT NULL,
  output_pkts INTEGER NOT NULL,
  output_bytes INTEGER NOT NULL,

  five_min_input_bps INTEGER,
  five_min_input_pps INTEGER,
  five_min_output_bps INTEGER,
  five_min_output_pps INTEGER
);

CREATE INDEX IF NOT EXISTS idx_interface_samples_device_iface_ts
  ON interface_samples(device, iface, ts_utc);
"""


def ensure_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()


def insert_sample(db_path: str, device: str, counters: InterfaceCounters, ts_utc: str | None = None) -> None:
    if ts_utc is None:
        ts_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO interface_samples (
              ts_utc, device, iface,
              input_pkts, input_bytes, output_pkts, output_bytes,
              five_min_input_bps, five_min_input_pps, five_min_output_bps, five_min_output_pps
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ts_utc, device, counters.iface,
                counters.input_pkts, counters.input_bytes,
                counters.output_pkts, counters.output_bytes,
                counters.five_min_input_bps, counters.five_min_input_pps,
                counters.five_min_output_bps, counters.five_min_output_pps,
            ),
        )
        conn.commit()
