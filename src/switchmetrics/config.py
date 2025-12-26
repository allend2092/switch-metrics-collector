from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Config:
    switch_host: str
    switch_username: str
    switch_password: str
    switch_name: str
    interfaces: list[str]
    raw_dir: str
    db_path: str

def load_config() -> Config:
    switch_host = os.environ["SWITCH_HOST"]
    switch_username = os.environ["SWITCH_USERNAME"]
    switch_password = os.environ["SWITCH_PASSWORD"]
    switch_name = os.getenv("SWITCH_NAME", switch_host)

    interfaces_csv = os.getenv("INTERFACES", "")
    interfaces = [i.strip() for i in interfaces_csv.split(",") if i.strip()]
    if not interfaces:
        raise ValueError("INTERFACES is empty. Example: INTERFACES=fa0/45,fa0/47,fa0/48")

    raw_dir = os.getenv("RAW_DIR", "data/raw")
    db_path = os.getenv("DB_PATH", "data/db/switchmetrics.sqlite3")

    return Config(
        switch_host=switch_host,
        switch_username=switch_username,
        switch_password=switch_password,
        switch_name=switch_name,
        interfaces=interfaces,
        raw_dir=raw_dir,
        db_path=db_path,
    )
