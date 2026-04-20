from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from trading_logic import build_decision, save_decision


OUTPUT_PATH = Path("data.json")


def main() -> None:
    decision = build_decision()
    save_decision(decision, OUTPUT_PATH)
    print(json.dumps(asdict(decision)))


if __name__ == "__main__":
    main()
