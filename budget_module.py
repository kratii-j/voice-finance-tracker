"""Helpers for reading budget limits and generating alert messages."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from config import BUDGETS_FILE, DEFAULT_BUDGET_WARN_THRESHOLD
from database import get_monthly_totals_by_category
from logger import log_error, log_info


@dataclass
class BudgetLimit:
    category: str
    limit: float
    warn_ratio: float

    @property
    def warn_amount(self) -> float:
        return self.limit * self.warn_ratio


@dataclass
class BudgetStatus:
    category: str
    limit: float
    spent: float
    remaining: float
    percentage: float
    level: str
    message: str


_DEFAULT_BUDGETS: Dict[str, Dict[str, Dict[str, float]]] = {
    "monthly": {
        "food": {"limit": 10000, "warn_at": 0.8},
        "transport": {"limit": 4000, "warn_at": 0.75},
        "entertainment": {"limit": 3000, "warn_at": 0.8},
        "utilities": {"limit": 5000, "warn_at": 0.8},
        "uncategorized": {"limit": 2000, "warn_at": 0.9},
    },
    "defaults": {"warn_at": DEFAULT_BUDGET_WARN_THRESHOLD},
}


def _ensure_budget_file(path: str = BUDGETS_FILE) -> None:
    if os.path.exists(path):
        return
    try:
        with open(path, "w", encoding="ascii") as handle:
            json.dump(_DEFAULT_BUDGETS, handle, indent=2)
        log_info("Created default budget configuration at %s", path)
    except OSError as exc:
        log_error("Failed to create default budgets: %s", exc)


def load_budget_config(path: str = BUDGETS_FILE) -> Dict[str, Dict[str, Dict[str, float]]]:
    _ensure_budget_file(path)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            config = json.load(handle)
    except FileNotFoundError:
        log_error("Budget file %s missing after ensure step", path)
        return _DEFAULT_BUDGETS
    except json.JSONDecodeError as exc:
        log_error("Budget file %s invalid JSON: %s", path, exc)
        return _DEFAULT_BUDGETS
    defaults = config.get("defaults", {})
    if "warn_at" not in defaults:
        defaults["warn_at"] = DEFAULT_BUDGET_WARN_THRESHOLD
    config["defaults"] = defaults
    return config


def _to_budget_limits(config: Dict[str, Dict[str, Dict[str, float]]]) -> Dict[str, BudgetLimit]:
    defaults = config.get("defaults", {})
    default_warn_ratio = float(defaults.get("warn_at", DEFAULT_BUDGET_WARN_THRESHOLD))
    budgets: Dict[str, BudgetLimit] = {}
    for category, payload in config.get("monthly", {}).items():
        limit = float(payload.get("limit", 0))
        if limit <= 0:
            continue
        warn_ratio = float(payload.get("warn_at", default_warn_ratio))
        warn_ratio = min(max(warn_ratio, 0.0), 1.0)
        budgets[category.lower()] = BudgetLimit(category=category.lower(), limit=limit, warn_ratio=warn_ratio)
    return budgets


def get_budget_limits() -> Dict[str, BudgetLimit]:
    config = load_budget_config()
    return _to_budget_limits(config)


def _assess_single_budget(spent: float, limit: BudgetLimit) -> BudgetStatus:
    percentage = spent / limit.limit if limit.limit else 0.0
    remaining = max(limit.limit - spent, 0.0)
    warn_amount = limit.warn_amount
    if spent >= limit.limit:
        level = "critical"
        message = f"Budget for {limit.category} exceeded. Spent ₹{spent:.0f} out of ₹{limit.limit:.0f}."
    elif spent >= warn_amount:
        level = "warning"
        message = (
            f"Budget for {limit.category} close to limit: ₹{spent:.0f} used, "
            f"₹{remaining:.0f} remaining."
        )
    else:
        level = "ok"
        message = f"Budget for {limit.category} is healthy with ₹{remaining:.0f} remaining."
    return BudgetStatus(
        category=limit.category,
        limit=limit.limit,
        spent=spent,
        remaining=remaining,
        percentage=percentage,
        level=level,
        message=message,
    )


def evaluate_monthly_budgets(year: Optional[int] = None, month: Optional[int] = None) -> List[BudgetStatus]:
    now = datetime.now()
    year = year or now.year
    month = month or now.month
    limits = get_budget_limits()
    if not limits:
        return []
    totals = get_monthly_totals_by_category(year=year, month=month)
    spending = {row["category"].lower(): float(row["total"]) for row in totals}
    results: List[BudgetStatus] = []
    for category, limit in limits.items():
        spent = spending.get(category, 0.0)
        results.append(_assess_single_budget(spent, limit))
    return results


def get_alert_for_category(category: str, year: Optional[int] = None, month: Optional[int] = None) -> Optional[BudgetStatus]:
    category_key = category.lower()
    limits = get_budget_limits()
    limit = limits.get(category_key)
    if not limit:
        return None
    statuses = evaluate_monthly_budgets(year=year, month=month)
    for status in statuses:
        if status.category == category_key and status.level in {"warning", "critical"}:
            return status
    return None


def summarize_alerts(statuses: List[BudgetStatus]) -> List[str]:
    return [status.message for status in statuses if status.level in {"warning", "critical"}]


__all__ = [
    "BudgetLimit",
    "BudgetStatus",
    "evaluate_monthly_budgets",
    "get_alert_for_category",
    "get_budget_limits",
    "load_budget_config",
    "summarize_alerts",
]
