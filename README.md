# Switch Metrics Collector

A lightweight Python application that collects interface counters from a Cisco IOS switch via SSH, stores time-series samples locally, and computes traffic deltas and rates.

This project is intentionally built in **phases**, starting with a minimal, resource-efficient design suitable for constrained systems (e.g., Raspberry Pi 3), while keeping a clear upgrade path toward more advanced observability stacks.

---

## Project Goals

- Collect **monotonic interface counters** (bytes, packets) from Cisco IOS devices
- Persist samples locally in a simple, inspectable format
- Compute **deltas and derived rates** (bps) from stored samples
- Keep the Phase 1 footprint small and transparent
- Provide a foundation that can later evolve into:
  - scheduled collection (cron)
  - retention policies
  - containerization
  - time-series databases (Postgres / TimescaleDB / InfluxDB)
  - visualization (Grafana)

---

## Current State (Phase 1)

**What works today:**

- SSH collection using `netmiko`
- Raw CLI output is saved to disk for auditability
- Deterministic parsing of `show interfaces <iface>` output
- Storage of per-interface samples in SQLite
- Computation of per-interface deltas and derived bit-rates
- Clean CLI entrypoint (`switchmetrics`)

Each execution:
1. Connects to the switch
2. Runs `show interfaces` for a configured interface list
3. Saves raw output under `data/raw/<device>/<timestamp>/`
4. Parses counters into structured fields
5. Inserts samples into a local SQLite database
6. Computes and prints deltas from the previous sample

---

## Example Output

```text
[OK] Saved raw outputs to: data/raw/Cat_3560-PoE/20251226T230114Z
[OK] FastEthernet0/45: in_bytes=181029 out_bytes=13489175 (5m in/out bps=0/1000)
[OK] FastEthernet0/47: in_bytes=17028210 out_bytes=918357280 (5m in/out bps=1000/8000)
[OK] FastEthernet0/48: in_bytes=4364445042 out_bytes=88951912 (5m in/out bps=10000/2000)
[OK] Inserted 3 samples into data/db/switchmetrics.sqlite3
[DELTA] FastEthernet0/45 over 278.0s: in=552B (15.9 bps) out=112747B (3244.5 bps)
[DELTA] FastEthernet0/47 over 278.0s: in=136855B (3938.3 bps) out=744064B (21411.9 bps)
[DELTA] FastEthernet0/48 over 278.0s: in=782377B (22514.4 bps) out=181185B (5214.0 bps)
```

## Requirements  
  
Python 3.10+  
Network access to a Cisco IOS device  
SSH enabled on the switch  
Tested against:  
Cisco Catalyst 3560 (IOS 12.2(55)SE)  
  
## Installation
  
Create a virtual environment and install in editable mode:  
```
python3 -m venv .switch_metrics
source .switch_metrics/bin/activate
pip install -e .
```
  
## Configuration
  
Create a .env file (this file is not committed to Git):  
  
SWITCH_HOST=10.1.2.3  
SWITCH_USERNAME=your_username  
SWITCH_PASSWORD=your_password  
SWITCH_NAME=Cat_3560-PoE  
INTERFACES=fa0/45,fa0/47,fa0/48  
  
  
An example template is provided in .env.example  

  
## Usage

Run a single collection + report cycle:  
```
switchmetrics
```

Or equivalently:    
  
```python -m switchmetrics.cli```
  
To observe meaningful rates, run the command twice with a delay:  
```  
switchmetrics
sleep 60
switchmetrics
```
