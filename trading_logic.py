from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import yfinance as yf


OUTPUT_PATH = Path("latest_decision.json")


@dataclass(frozen=True)
class TradingDecision:
    qqq: float
    tqqq: float
    scenario: str
    action: str
    timestamp: str


SCENARIO_RULES = (
    (700.0, "Strong Bull", "Sell TQQQ spreads, roll short calls higher"),
    (680.0, "Bull", "Prepare to roll calls, optional trim of TQQQ spreads"),
    (630.0, "Neutral", "DO NOTHING"),
    (600.0, "Weak", "Reduce risk and avoid new leverage"),
    (580.0, "Danger", "Close TQQQ spreads, take hedge profits"),
    (float("-inf"), "Crash", "Exit leveraged exposure"),
)


NOTES_BY_SCENARIO = {
    "Strong Bull": "Momentum is very strong. Favor offense, but keep position sizing disciplined.",
    "Bull": "Trend is constructive. Adding exposure can make sense if the move remains orderly.",
    "Neutral": "No edge from the regime alone. Staying patient is usually better than forcing trades.",
    "Weak": "Trend quality is deteriorating. Prefer defense over fresh leveraged entries.",
    "Danger": "Market conditions are fragile. Capital preservation matters more than upside capture.",
    "Crash": "High-risk regime. Leveraged long exposure is inappropriate until conditions improve.",
}


def fetch_last_price(symbol: str) -> float:
    ticker = yf.Ticker(symbol)
    history = ticker.history(period="5d", interval="1d", auto_adjust=False)
    if history.empty:
        raise ValueError(f"No price data returned for {symbol}.")

    close = history["Close"].dropna()
    if close.empty:
        raise ValueError(f"No closing prices returned for {symbol}.")

    return round(float(close.iloc[-1]), 2)


def classify_scenario(qqq_price: float) -> tuple[str, str]:
    if qqq_price >= 700.0:
        return SCENARIO_RULES[0][1], SCENARIO_RULES[0][2]

    if qqq_price >= 680.0:
        return SCENARIO_RULES[1][1], SCENARIO_RULES[1][2]

    for threshold, scenario, action in SCENARIO_RULES:
        if threshold >= 680.0:
            continue
        if qqq_price > threshold:
            return scenario, action
    raise RuntimeError("Failed to classify scenario.")


def build_decision() -> TradingDecision:
    qqq_price = fetch_last_price("QQQ")
    tqqq_price = fetch_last_price("TQQQ")
    scenario, action = classify_scenario(qqq_price)

    return TradingDecision(
        qqq=qqq_price,
        tqqq=tqqq_price,
        scenario=scenario,
        action=action,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def notes_for_scenario(scenario: str) -> str:
    return NOTES_BY_SCENARIO.get(scenario, "No notes available for this scenario.")


def save_decision(decision: TradingDecision, path: Path = OUTPUT_PATH) -> None:
    path.write_text(json.dumps(asdict(decision), indent=2), encoding="utf-8")


def load_saved_decision(path: Path = OUTPUT_PATH) -> TradingDecision | None:
    if not path.exists():
        return None

    raw = json.loads(path.read_text(encoding="utf-8"))
    return TradingDecision(**raw)
