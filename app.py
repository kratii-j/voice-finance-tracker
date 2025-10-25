import os
from typing import Optional
from flask import Flask, jsonify, render_template, request

from database import add_expense, get_recent_expenses, get_total_by_category, get_total_today
from summary_module import (
    get_monthly_summary_text,
    get_monthly_total,
    get_weekly_summary_text,
)
from visual_module_updated import ensure_chart_dir, generate_all_charts
from logger import log_error, log_info

app = Flask(__name__, static_folder="static", template_folder="templates")
ensure_chart_dir()  # make sure chart directory exists at startup


def _to_static_path(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    rel = os.path.relpath(path, "static")
    return rel.replace(os.sep, "/")


def _build_dashboard_context():
    charts = generate_all_charts()
    return {
        "total_today": get_total_today(),
        "monthly_total": get_monthly_total(),
        "category_totals": get_total_by_category(),
        "recent_expenses": get_recent_expenses(5),
        "weekly_summary": get_weekly_summary_text(),
        "monthly_summary": get_monthly_summary_text(),
        "charts": {
            key: _to_static_path(path)
            for key, path in charts.items()
        },
    }


@app.route("/")
def index():
    context = _build_dashboard_context()
    return render_template("index.html", **context)


@app.route("/api/summary")
def api_summary():
    context = _build_dashboard_context()
    return jsonify(
        total_today=context["total_today"],
        weekly_summary=context["weekly_summary"],
        monthly_summary=context["monthly_summary"],
        category_totals=context["category_totals"],
    )


@app.route("/api/recent")
def api_recent():
    limit = int(request.args.get("limit", 5))
    return jsonify(get_recent_expenses(limit))


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


if __name__ == "__main__":
    app.run(debug=True)
