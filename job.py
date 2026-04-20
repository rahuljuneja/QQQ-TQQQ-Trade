from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from trading_logic import build_decision


OUTPUT_PATH = Path("data.json")
STATE_PATH = Path("state.json")
STARTING_CAPITAL = 10000.0
QQQ_SHARES = 9


def load_previous_data() -> dict | None:
    if not OUTPUT_PATH.exists():
        return None

    return json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {}

    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def determine_change(
    prev_scenario: str | None,
    prev_action: str | None,
    current_scenario: str,
    current_action: str,
) -> str:
    if prev_scenario is None and prev_action is None:
        return "INITIAL"

    if prev_scenario != current_scenario:
        return "SCENARIO_CHANGED"

    if prev_action != current_action:
        return "ACTION_CHANGED"

    return "NO_CHANGE"


def main() -> None:
    previous = load_previous_data()
    state = load_state()
    decision = build_decision()
    payload = asdict(decision)
    qqq_entry_price = float(state.get("qqq_entry_price", decision.qqq))
    qqq_value = QQQ_SHARES * decision.qqq
    position_cost = qqq_entry_price * QQQ_SHARES
    pnl = qqq_value - position_cost
    portfolio_value = STARTING_CAPITAL + pnl
    pnl_percent = (pnl / STARTING_CAPITAL) * 100

    prev_scenario = previous.get("scenario") if previous else None
    prev_action = previous.get("action") if previous else None

    payload["prev_scenario"] = prev_scenario
    payload["prev_action"] = prev_action
    payload["change"] = determine_change(
        prev_scenario=prev_scenario,
        prev_action=prev_action,
        current_scenario=decision.scenario,
        current_action=decision.action,
    )
    payload["portfolio_value"] = round(portfolio_value, 2)
    payload["pnl"] = round(pnl, 2)
    payload["pnl_percent"] = round(pnl_percent, 2)

    save_state({"qqq_entry_price": qqq_entry_price})

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
