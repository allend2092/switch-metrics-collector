from __future__ import annotations

import sqlite3
from datetime import datetime, timezone


def _parse_ts(ts_utc: str) -> datetime:
    # stored as "YYYY-MM-DDTHH:MM:SSZ"
    return datetime.strptime(ts_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def report_last_delta(db_path: str, device: str) -> int:
    """
    Prints the most recent delta (and derived bps) per interface.
    Returns non-zero if insufficient data.
    """
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row

        # Find interfaces we have for this device
        ifaces = [r["iface"] for r in conn.execute(
            "SELECT DISTINCT iface FROM interface_samples WHERE device=? ORDER BY iface",
            (device,),
        ).fetchall()]

        if not ifaces:
            print("[WARN] No interfaces found in DB.")
            return 2

        any_insufficient = False

        for iface in ifaces:
            rows = conn.execute(
                """
                SELECT ts_utc, input_bytes, output_bytes
                FROM interface_samples
                WHERE device=? AND iface=?
                ORDER BY ts_utc DESC
                LIMIT 2
                """,
                (device, iface),
            ).fetchall()

            if len(rows) < 2:
                print(f"[WARN] {iface}: only {len(rows)} sample(s); need 2 for delta.")
                any_insufficient = True
                continue

            newest, prev = rows[0], rows[1]

            t_new = _parse_ts(newest["ts_utc"])
            t_prev = _parse_ts(prev["ts_utc"])
            delta_s = (t_new - t_prev).total_seconds()

            if delta_s <= 0:
                print(f"[WARN] {iface}: non-positive delta time ({delta_s}).")
                any_insufficient = True
                continue

            din = newest["input_bytes"] - prev["input_bytes"]
            dout = newest["output_bytes"] - prev["output_bytes"]

            # Handle counter resets (e.g., interface reset, reload)
            if din < 0 or dout < 0:
                print(f"[WARN] {iface}: counter reset detected (din={din}, dout={dout}).")
                any_insufficient = True
                continue

            bps_in = (din * 8.0) / delta_s
            bps_out = (dout * 8.0) / delta_s

            print(
                f"[DELTA] {iface} over {delta_s:.1f}s: "
                f"in={din}B ({bps_in:.1f} bps) out={dout}B ({bps_out:.1f} bps)"
            )

        return 1 if any_insufficient else 0
