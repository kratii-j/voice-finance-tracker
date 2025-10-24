from flask import Flask, render_template, request, jsonify, send_from_directory
from visual_module_updated import (
    get_weekly_summary_text,
    get_monthly_summary_text,
    generate_all_charts,
    ensure_chart_dir,
)
from database import add_expense, get_total_today
import os

app = Flask(__name__)
ensure_chart_dir()


@app.route("/charts/<path:filename>")
def serve_chart_file(filename):
    """Serve static chart images."""
    return send_from_directory("static/charts", filename)


@app.route("/")
def index():
    """Render the main dashboard page."""
    weekly_text = get_weekly_summary_text()
    monthly_text = get_monthly_summary_text()
    charts = generate_all_charts()

    charts_for_template = {
        key: os.path.basename(path) if path else None
        for key, path in charts.items()
    }

    total = 0.0
    for line in monthly_text.split("\n"):
        if "Total spent" in line:
            try:
                total = float(line.split("₹")[-1])
            except:
                pass

    return render_template(
        "index.html",
        total=total,
        weekly_text=weekly_text,
        monthly_text=monthly_text,
        charts=charts_for_template,
    )


@app.route("/api/add", methods=["POST"])
def add_expense_api():
    """Add an expense from frontend form (AJAX)."""
    data = request.json
    amount = data.get("amount")
    category = data.get("category")

    if not amount or not category:
        return jsonify({"error": "Missing fields"}), 400

    try:
        add_expense(float(amount), category)
        total_today = get_total_today()
        return jsonify(
            {
                "message": f"Added ₹{amount} to {category}.",
                "total_today": total_today,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
