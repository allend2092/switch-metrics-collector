from __future__ import annotations

import os
from dotenv import load_dotenv

from .config import load_config
from .collect import collect_show_interfaces, save_raw_outputs
from .parse_ios_show_int import parse_show_interfaces
from .store_sqlite import ensure_db, insert_sample
from .report import report_last_delta

#print("[DEBUG] entered main()")

def main() -> None:
    load_dotenv()  # loads .env if present

    cfg = load_config()
    ensure_db(cfg.db_path)

    outputs = collect_show_interfaces(cfg)
    raw_dir = save_raw_outputs(cfg, outputs)

    print(f"[OK] Saved raw outputs to: {raw_dir}")

    for iface, raw in outputs.items():
        counters = parse_show_interfaces(raw)
        insert_sample(cfg.db_path, cfg.switch_name, counters)
        print(
            f"[OK] {counters.iface}: in_bytes={counters.input_bytes} out_bytes={counters.output_bytes} "
            f"(5m in/out bps={counters.five_min_input_bps}/{counters.five_min_output_bps})"
        )

    print(f"[OK] Inserted {len(outputs)} samples into {cfg.db_path}")
    report_last_delta(cfg.db_path, cfg.switch_name)

if __name__ == "__main__":
    main()
