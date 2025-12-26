from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class InterfaceCounters:
    iface: str
    admin_line: str  # e.g. "FastEthernet0/47 is up, line protocol is up (connected)"
    input_pkts: int
    input_bytes: int
    output_pkts: int
    output_bytes: int
    five_min_input_bps: Optional[int]
    five_min_input_pps: Optional[int]
    five_min_output_bps: Optional[int]
    five_min_output_pps: Optional[int]


_RE_FIRST_LINE = re.compile(r"^(?P<iface>\S+) is .+$", re.MULTILINE)

_RE_5MIN_IN = re.compile(r"^  5 minute input rate (?P<bps>\d+) bits/sec, (?P<pps>\d+) packets/sec$", re.MULTILINE)
_RE_5MIN_OUT = re.compile(r"^  5 minute output rate (?P<bps>\d+) bits/sec, (?P<pps>\d+) packets/sec$", re.MULTILINE)

_RE_INPUT = re.compile(r"^\s*(?P<pkts>\d+)\s+packets input,\s+(?P<bytes>\d+)\s+bytes,", re.MULTILINE)
_RE_OUTPUT = re.compile(r"^\s*(?P<pkts>\d+)\s+packets output,\s+(?P<bytes>\d+)\s+bytes,", re.MULTILINE)


def parse_show_interfaces(raw: str) -> InterfaceCounters:
    m0 = _RE_FIRST_LINE.search(raw)
    if not m0:
        raise ValueError("Could not find interface first line (e.g., 'FastEthernet0/47 is up...').")

    iface = m0.group("iface")
    admin_line = m0.group(0).strip()

    mi = _RE_INPUT.search(raw)
    mo = _RE_OUTPUT.search(raw)
    if not mi or not mo:
        raise ValueError(f"Could not find input/output counters for {iface}.")

    m_in = _RE_5MIN_IN.search(raw)
    m_out = _RE_5MIN_OUT.search(raw)

    return InterfaceCounters(
        iface=iface,
        admin_line=admin_line,
        input_pkts=int(mi.group("pkts")),
        input_bytes=int(mi.group("bytes")),
        output_pkts=int(mo.group("pkts")),
        output_bytes=int(mo.group("bytes")),
        five_min_input_bps=int(m_in.group("bps")) if m_in else None,
        five_min_input_pps=int(m_in.group("pps")) if m_in else None,
        five_min_output_bps=int(m_out.group("bps")) if m_out else None,
        five_min_output_pps=int(m_out.group("pps")) if m_out else None,
    )
