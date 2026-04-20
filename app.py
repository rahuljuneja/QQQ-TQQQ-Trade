from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from os import getenv
from pathlib import Path

import streamlit as st

from trading_logic import load_saved_decision, notes_for_scenario


DATA_PATH = Path("data.json")


st.set_page_config(page_title="Daily Trading Decision Dashboard", page_icon="📈", layout="centered")


def load_decision():
    cached = load_saved_decision(DATA_PATH)
    if cached is not None:
        return cached

    subprocess.run([sys.executable, "job.py"], check=True)
    generated = load_saved_decision(DATA_PATH)
    if generated is None:
        raise ValueError("job.py completed but data.json was not created.")
    return generated


def main() -> None:
    try:
        decision = load_decision()
    except Exception as exc:
        st.title("Daily Trading Decision Dashboard")
        st.error(f"Unable to load market data: {exc}")
        st.stop()

    notes = notes_for_scenario(decision.scenario)
    timestamp = datetime.fromisoformat(decision.timestamp.replace("Z", "+00:00"))

    st.title("Daily Trading Decision Dashboard")
    st.caption(f"Serving on port {getenv('PORT', '8501')}")

    qqq_col, tqqq_col = st.columns(2)
    qqq_col.metric("QQQ", f"${decision.qqq:,.2f}")
    tqqq_col.metric("TQQQ", f"${decision.tqqq:,.2f}")

    st.subheader(f"Scenario: {decision.scenario}")
    st.markdown(
        f"""
        <div style="padding: 1.5rem 1rem; border-radius: 0.75rem; background: #111827; text-align: center;">
            <div style="font-size: 1rem; color: #9ca3af; letter-spacing: 0.2em;">ACTION</div>
            <div style="font-size: 2.4rem; font-weight: 800; color: #f9fafb; margin-top: 0.5rem;">
                {decision.action}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Notes")
    st.write(notes)

    st.caption(f"Last updated: {timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')} from data.json")


if __name__ == "__main__":
    main()
