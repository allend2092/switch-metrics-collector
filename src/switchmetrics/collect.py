from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from netmiko import ConnectHandler

from .config import Config


def utc_ts_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def collect_show_interfaces(cfg: Config) -> Dict[str, str]:
    """
    Returns: { "fa0/45": "<raw output>", ... }
    """
    device = {
        "device_type": "cisco_ios",
        "host": cfg.switch_host,
        "username": cfg.switch_username,
        "password": cfg.switch_password,
        # 3560 often doesn't need enable for show, but you can add 'secret' later if needed
    }

    outputs: Dict[str, str] = {}
    with ConnectHandler(**device) as conn:
        # Optional: speed + deterministic output
        conn.send_command("terminal length 0")
        for iface in cfg.interfaces:
            cmd = f"show interfaces {iface}"
            raw = conn.send_command(cmd)
            outputs[iface] = raw

    return outputs


def save_raw_outputs(cfg: Config, outputs: Dict[str, str]) -> Path:
    """
    Writes one file per interface under data/raw/<switch_name>/<timestamp>/show_interfaces_<iface>.txt
    """
    ts = utc_ts_compact()
    base = Path(cfg.raw_dir) / cfg.switch_name / ts
    base.mkdir(parents=True, exist_ok=True)

    for iface, raw in outputs.items():
        safe_iface = iface.replace("/", "_")
        p = base / f"show_interfaces_{safe_iface}.txt"
        p.write_text(raw + "\n", encoding="utf-8")

    return base
