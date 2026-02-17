from __future__ import annotations

import io
import os
from datetime import datetime
from flask import Flask, render_template, request, send_file, flash, jsonify, Response

from services.media_planner import build_media_plan
from services.pdf_export import render_media_plan_pdf


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")


def _is_tilda_test_payload() -> bool:
    """Tilda sends `test=test` during webhook connection check."""
    raw_body = request.get_data(as_text=True).strip()
    return request.form.get("test") == "test" or raw_body == "test=test"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    # Graceful response for accidental webhook checks pointed to `/`.
    if _is_tilda_test_payload():
        return jsonify({"status": "ok", "message": "tilda webhook test accepted"}), 200

    niche = request.form.get("niche", "").strip()
    region = request.form.get("region", "Россия").strip()
    budget = request.form.get("budget", "").strip()
    objective = request.form.get("objective", "Лиды").strip()

    if not niche:
        flash("Введите описание ниши.")
        return render_template("index.html")

    try:
        budget_value = float(budget.replace(",", ".")) if budget else 0.0
    except ValueError:
        flash("Бюджет должен быть числом.")
        return render_template("index.html")

    plan = build_media_plan(
        niche_description=niche,
        region=region,
        monthly_budget=budget_value,
        objective=objective,
    )

    pdf_bytes = render_media_plan_pdf(plan)
    filename = f"mediaplan_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    return send_file(
        io.BytesIO(pdf_bytes),
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf",
    )


@app.route("/webhook/tilda", methods=["POST"])
def tilda_webhook():
    """
    Generic webhook endpoint for Tilda forms.
    Must return 200 for `test=test` payload during connection check.
    """
    if _is_tilda_test_payload():
        return Response("ok", status=200, mimetype="text/plain")

    # Accept both form and JSON payloads.
    payload = request.get_json(silent=True) or request.form.to_dict(flat=True)

    # Keep response lightweight: Tilda expects fast 200 OK responses.
    # In production, pass payload to background worker/queue here.
    _ = payload
    return Response("ok", status=200, mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
