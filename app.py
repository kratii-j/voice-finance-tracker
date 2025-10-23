from flask import Flask, render_template, send_from_directory
from visual_module_updated import (
    get_weekly_summary_text,
    get_monthly_summary_text,
    generate_all_charts,
    ensure_chart_dir,
)
import os

app = Flask(__name__)
ensure_chart_dir()  

@app.route("/charts/<path:filename>")
def serve_chart_file(filename):
    return send_from_directory("static/charts", filename)

@app.route("/")
def index():
    weekly_text = get_weekly_summary_text()
    monthly_text = get_monthly_summary_text()

    charts = generate_all_charts()  
    charts_for_template = {}
    for key, path in charts.items():
        if path:
            charts_for_template[key] = os.path.basename(path)
        else:
            charts_for_template[key] = None

    total = 0.0
    lines = monthly_text.split("\n")
    if lines:
        last_line = lines[-1]
        if "Total spent" in last_line:
            try:
                total = float(last_line.split("₹")[-1])
            except:
                total = 0.0

    return render_template(
        "index.html",
        total=total,
        weekly_text=weekly_text,
        monthly_text=monthly_text,
        charts=charts_for_template,
    )

if __name__ == "__main__":
    app.run(debug=True)
