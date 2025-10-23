from flask import Flask, render_template, send_from_directory
from visual_module_updated import generate_weekly_summary, generate_monthly_summary
import os

app = Flask(__name__)

@app.route("/charts/<path:filename>")
def serve_chart_file(filename):
    charts_dir = os.path.join(app.root_path, "static", "charts")
    return send_from_directory(charts_dir, filename)


@app.route("/")
def home():
    weekly_text, weekly_chart = generate_weekly_summary()
    monthly_text, monthly_chart, timeseries_chart = generate_monthly_summary()

    charts = {
        "weekly_category": os.path.basename(weekly_chart) if weekly_chart else None,
        "monthly_category": os.path.basename(monthly_chart) if monthly_chart else None,
        "timeseries": os.path.basename(timeseries_chart) if timeseries_chart else None,
    }

    total = 0

    return render_template(
        "index.html",
        weekly_text=weekly_text,
        monthly_text=monthly_text,
        total=total,
        charts=charts,
    )


if __name__ == "__main__":
    app.run(debug=True)
