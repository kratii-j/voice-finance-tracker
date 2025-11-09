import os
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from budget_module import (
    evaluate_monthly_budgets,
    format_budget_summary,
    get_alert_for_category,
    get_budget_limits,
    summarize_alerts,
)
from config import DATE_FORMAT, REACT_BUILD_DIR, REACT_INDEX_FILE
from database import (
    add_expense,
    delete_last_expense,
    get_recent_expenses,
    get_total_by_category,
    get_total_today,
)
from summary_module import (
    get_monthly_summary_text,
    get_monthly_total,
    get_weekly_summary_text,
)
from visual_module import (
    ensure_chart_dir,
    generate_all_charts,
    get_category_breakdown,
    get_monthly_totals_by_month,
    get_recent_daily_totals,
)
from logger import log_error, log_info
# Defer importing heavy voice/audio-related code until it's needed to avoid
# import-time side-effects (pyttsx3, speech_recognition, sounddevice).
parse_expense = None

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)  # allow frontend dev server to reach the API
ensure_chart_dir()  # make sure chart directory exists at startup

VOICE_HELP_TEXT = (
    "Try commands like:\n"
    "- Add 200 to food\n"
    "- What's my balance today\n"
    "- Show recent expenses\n"
    "- Give weekly summary\n"
    "- Delete last expense\n"
    "- Set budget for food to 5000\n"
    "- What's my budget / Show budgets\n"
    "- Stop to exit"
)


def _to_static_path(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    rel = os.path.relpath(path, "static")
    return rel.replace(os.sep, "/")


def _react_build_exists() -> bool:
    return os.path.isfile(REACT_INDEX_FILE)


def _serve_react_asset(path: Optional[str] = None):
    if not _react_build_exists():
        return None
    relative_path = (path or "").strip()
    if relative_path:
        candidate = os.path.join(REACT_BUILD_DIR, relative_path)
        if os.path.isfile(candidate):
            return send_from_directory(REACT_BUILD_DIR, relative_path)
    return send_from_directory(REACT_BUILD_DIR, "index.html")


def _serialize_category_breakdown() -> Dict[str, Any]:
    df = get_category_breakdown()
    if df.empty:
        return {"items": []}
    items = [
        {"category": str(row["category"]), "total": float(row["total"])}
        for _, row in df.iterrows()
    ]
    return {"items": items}


def _serialize_daily_totals(days: int = 7) -> Dict[str, Any]:
    df = get_recent_daily_totals(days)
    totals_by_date = {
        str(row["date"]): float(row["total"])
        for _, row in df.iterrows()
    }
    today = datetime.now().date()
    start_date = today - timedelta(days=days - 1)
    series = []
    for offset in range(days):
        current = start_date + timedelta(days=offset)
        key = current.strftime(DATE_FORMAT)
        series.append(
            {
                "date": key,
                "label": current.strftime("%a"),
                "total": totals_by_date.get(key, 0.0),
            }
        )
    return {"items": series}


def _serialize_monthly_totals(months: int = 6) -> Dict[str, Any]:
    df = get_monthly_totals_by_month(months)
    totals_by_month = {
        str(row["month"]): float(row["total"])
        for _, row in df.iterrows()
    }
    first_of_month = datetime.now().replace(day=1)
    months_sequence = []
    current = first_of_month
    for _ in range(max(months, 1)):
        months_sequence.append(current)
        if current.month == 1:
            current = current.replace(year=current.year - 1, month=12)
        else:
            current = current.replace(month=current.month - 1)
    months_sequence.reverse()
    series = []
    for month_date in months_sequence:
        key = month_date.strftime("%Y-%m")
        series.append(
            {
                "month": key,
                "label": month_date.strftime("%b %Y"),
                "total": totals_by_month.get(key, 0.0),
            }
        )
    return {"items": series}


def _build_chart_series(days: int = 7, months: int = 6) -> Dict[str, Any]:
    """Compile chart-friendly aggregates for API consumers."""
    return {
        "category_breakdown": _serialize_category_breakdown()["items"],
        "daily_totals": _serialize_daily_totals(days)["items"],
        "monthly_totals": _serialize_monthly_totals(months)["items"],
    }


def _safe_limit(value: Any, default: int = 5, *, minimum: int = 1, maximum: int = 50) -> int:
    try:
        numeric = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(numeric, maximum))


def _build_dashboard_context():
    charts = generate_all_charts()
    budget_statuses = evaluate_monthly_budgets()
    return {
        "total_today": get_total_today(),
        "monthly_total": get_monthly_total(),
        "category_totals": get_total_by_category(),
        "recent_expenses": get_recent_expenses(5),
        "weekly_summary": get_weekly_summary_text(),
        "monthly_summary": get_monthly_summary_text(),
        "budget_status": [
            {
                "category": status.category,
                "limit": status.limit,
                "spent": status.spent,
                "remaining": status.remaining,
                "percentage": status.percentage,
                "level": status.level,
                "message": status.message,
            }
            for status in budget_statuses
        ],
        "budget_alerts": summarize_alerts(budget_statuses),
        "charts": {
            key: _to_static_path(path)
            for key, path in charts.items()
        },
        "chart_series": _build_chart_series(),
    }


@app.route("/")
def index():
    response = _serve_react_asset()
    if response is not None:
        return response
    return jsonify(
        {
            "status": "react_build_missing",
            "message": "React build not found. Run `npm run build` inside the frontend/ directory.",
        }
    )


@app.route("/app", defaults={"path": ""})
@app.route("/app/<path:path>")
def serve_react_app(path: str):
    response = _serve_react_asset(path)
    if response is not None:
        return response
    return (
        jsonify(
            {
                "status": "react_build_missing",
                "message": "React build not found. Run `npm run build` inside the frontend/ directory.",
            }
        ),
        404,
    )


@app.route("/api/summary")
def api_summary():
    context = _build_dashboard_context()
    return jsonify(
        total_today=context["total_today"],
        weekly_summary=context["weekly_summary"],
        monthly_summary=context["monthly_summary"],
        category_totals=context["category_totals"],
        budget_alerts=context["budget_alerts"],
    )


@app.route("/api/recent")
def api_recent():
    limit = _safe_limit(request.args.get("limit"), default=5)
    return jsonify(get_recent_expenses(limit))


@app.route("/api/charts/category-breakdown")
def api_chart_category_breakdown():
    payload = _serialize_category_breakdown()
    # use timezone-aware UTC timestamp
    payload["generated_at"] = datetime.now(timezone.utc).isoformat()
    return jsonify(payload)


@app.route("/api/charts/daily-totals")
def api_chart_daily_totals():
    try:
        requested_days = int(request.args.get("days", 7))
    except (TypeError, ValueError):
        requested_days = 7
    days = max(1, min(requested_days, 90))
    payload = _serialize_daily_totals(days)
    # use timezone-aware UTC timestamp
    payload["generated_at"] = datetime.now(timezone.utc).isoformat()
    payload["days"] = days
    return jsonify(payload)


@app.route("/api/charts/monthly-totals")
def api_chart_monthly_totals():
    try:
        requested_months = int(request.args.get("months", 6))
    except (TypeError, ValueError):
        requested_months = 6
    months = max(1, min(requested_months, 24))
    payload = _serialize_monthly_totals(months)
    # use timezone-aware UTC timestamp
    payload["generated_at"] = datetime.now(timezone.utc).isoformat()
    payload["months"] = months
    return jsonify(payload)


@app.route("/api/regenerate-charts", methods=["POST"])
def api_regenerate_charts():
    try:
        charts = generate_all_charts()
        rel_paths = {key: _to_static_path(path) for key, path in charts.items()}
        log_info("Charts regenerated manually.")
        return jsonify({"status": "ok", "charts": rel_paths})
    except Exception as exc:
        log_error("Failed to regenerate charts: %s", exc)
        return jsonify({"status": "error"}), 500


@app.route("/api/add", methods=["POST"])
def api_add():
    data = request.get_json(silent=True) or {}
    try:
        amount = float(data.get("amount", 0))
        category = str(data.get("category", "")).strip()
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid amount or category."}), 400

    if amount <= 0 or not category:
        return jsonify({"error": "Amount must be positive and category required."}), 400

    try:
        expense_id = add_expense(amount, category)
        context = _build_dashboard_context()
        log_info("Expense added via API (id=%s)", expense_id)
        return jsonify(
            {
                "message": f"Added ₹{amount:.2f} to {category}.",
                "expense_id": expense_id,
                "total_today": context["total_today"],
                "monthly_total": context["monthly_total"],
            }
        )
    except Exception as exc:
        log_error("Add expense API failed: %s", exc)
        return jsonify({"error": "Failed to add expense."}), 500


def _refresh_dashboard() -> Dict[str, Any]:
    """Return a fresh snapshot of dashboard data for the frontend."""
    return _build_dashboard_context()


def _serialize_budget_status(statuses):
    return [asdict(status) for status in statuses]


@app.route("/api/voice_command", methods=["POST"])
def api_voice_command():
    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    command_text = str(payload.get("command", "")).strip()
    if not command_text:
        return jsonify({"error": "Command text required."}), 400

    # Import voice parsing lazily so the app can start in environments without
    # audio/Tk backends. The parsing function itself is pure text-processing
    # and does not require audio devices.
    try:
        global parse_expense  # type: ignore
        if parse_expense is None:
            from voice_module import parse_expense as _parse_fn  # local import
            parse_expense = _parse_fn  # cache for subsequent calls
        parsed = parse_expense(command_text)
    except Exception as exc:
        log_error("Failed to parse voice command: %s", exc)
        return jsonify({"error": "Could not understand the command."}), 500

    action = parsed.get("action", "unknown")
    response: Dict[str, Any] = {"action": action}

    if action == "none":
        response["reply"] = "I did not hear a command."
        return jsonify(response), 400

    if action == "unknown":
        response["reply"] = "I did not understand that. Try saying help."
        return jsonify(response)

    if action == "help":
        response["reply"] = VOICE_HELP_TEXT
        return jsonify(response)

    if action == "repeat":
        response["reply"] = "Repeat is not available in the web assistant."
        return jsonify(response)

    if action == "exit":
        response["reply"] = "The assistant stays ready. Say another command when you are ready."
        return jsonify(response)

    if action == "add":
        amount = parsed.get("amount")
        category = parsed.get("category") or "uncategorized"
        if amount is None or float(amount) <= 0:
            response["reply"] = "Please include a valid amount to add an expense."
            return jsonify(response), 400
        try:
            expense_id = add_expense(
                float(amount),
                category,
                date=parsed.get("date"),
                description=parsed.get("description"),
            )
            response["reply"] = f"Added ₹{float(amount):.2f} to {category}."
            response["expense_id"] = expense_id
            dashboard = _refresh_dashboard()
            response["dashboard"] = dashboard

            alert_year = alert_month = None
            if parsed.get("date"):
                try:
                    parsed_date = datetime.strptime(parsed["date"], DATE_FORMAT)
                    alert_year, alert_month = parsed_date.year, parsed_date.month
                except ValueError:
                    pass
            status = get_alert_for_category(category, year=alert_year, month=alert_month)
            if status:
                response["budget_alert"] = status.message
        except Exception as exc:
            log_error("Voice add expense failed: %s", exc)
            response["reply"] = "Failed to add the expense."
            return jsonify(response), 500
        return jsonify(response)

    if action == "delete":
        try:
            removed_id = delete_last_expense()
        except Exception as exc:
            log_error("Voice delete expense failed: %s", exc)
            response["reply"] = "Failed to delete the last expense."
            return jsonify(response), 500
        if not removed_id:
            response["reply"] = "No expense to delete."
            return jsonify(response)
        response["reply"] = f"Deleted expense number {removed_id}."
        response["deleted_expense_id"] = removed_id
        response["dashboard"] = _refresh_dashboard()
        return jsonify(response)

    if action == "balance":
        total_today = get_total_today()
        response["reply"] = f"Today's total spend is ₹{total_today:.2f}."
        response["total_today"] = total_today
        return jsonify(response)

    if action == "recent":
        limit = _safe_limit(payload.get("limit"), default=5)
        recent_items = get_recent_expenses(limit)
        response["reply"] = "Here are the most recent expenses."
        response["recent_expenses"] = recent_items
        return jsonify(response)

    if action == "weekly":
        summary_text = get_weekly_summary_text()
        response["reply"] = summary_text
        return jsonify(response)

    if action == "monthly":
        summary_text = get_monthly_summary_text()
        response["reply"] = summary_text
        response["budget_statuses"] = _serialize_budget_status(evaluate_monthly_budgets())
        return jsonify(response)

    if action == "show_budgets":
        category = parsed.get("category")
        if category:
            status = get_alert_for_category(category)
            if status:
                response["reply"] = status.message
                response["budget_status"] = asdict(status)
            else:
                limits = get_budget_limits()
                limit = limits.get(category.lower()) if category else None
                if limit:
                    response["reply"] = f"{category} budget is ₹{limit.limit:.0f} per month."
                    response["budget_limit"] = {
                        "category": limit.category,
                        "limit": limit.limit,
                        "warn_ratio": limit.warn_ratio,
                    }
                else:
                    response["reply"] = f"No budget configured for {category}."
        else:
            response["reply"] = format_budget_summary() or "No budgets configured."
            response["budget_statuses"] = _serialize_budget_status(evaluate_monthly_budgets())
        return jsonify(response)

    if action == "set_budget":
        response["reply"] = "Setting budgets from the web assistant is not available yet."
        return jsonify(response)

    response["reply"] = "That command is not supported yet."
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
