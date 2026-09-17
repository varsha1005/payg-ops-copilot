from __future__ import annotations

import pandas as pd


def dashboard_metrics(df: pd.DataFrame) -> dict:
    total = len(df)
    open_count = int((df["status"] != "Resolved").sum()) if total else 0
    urgent_high = int(df["priority"].isin(["Urgent", "High"]).sum()) if total else 0
    avg_resolution = round(float(df.loc[df["status"] == "Resolved", "resolution_hours"].mean()), 1) if (df["status"] == "Resolved").any() else 0.0
    ai_adoption = round(float(df["ai_used"].mean()) * 100, 1) if total else 0.0
    override_rate = round(float(df.loc[df["ai_used"] == 1, "human_override"].mean()) * 100, 1) if (df["ai_used"] == 1).any() else 0.0
    return {
        "tickets": total,
        "open": open_count,
        "high_or_urgent": urgent_high,
        "avg_resolution_hours": avg_resolution,
        "ai_adoption_pct": ai_adoption,
        "human_override_pct": override_rate,
    }
