from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import Flask, redirect, render_template, request, send_from_directory, url_for

from image_pipeline import process_image
from storage import fetch_records, init_db, insert_record


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
PROCESSED_DIR = BASE_DIR / "processed"

UPLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)
init_db()

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    latest_result = None

    if request.method == "POST":
        file = request.files.get("image")
        if not file or not file.filename:
            records = fetch_records()
            return render_template(
                "index.html",
                error="请选择一张图片后再提交。",
                latest_result=None,
                records=records,
            )

        suffix = Path(file.filename).suffix.lower() or ".jpg"
        saved_name = f"{uuid4().hex}{suffix}"
        upload_path = UPLOAD_DIR / saved_name
        file.save(upload_path)

        result = process_image(upload_path, PROCESSED_DIR)

        record = {
            "original_filename": saved_name,
            "processed_filename": result.processed_filename,
            "crop_filename": result.crop_filename,
            "plate_text": result.plate_text,
            "status": result.status,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        insert_record(record)
        latest_result = record

    records = fetch_records()
    return render_template(
        "index.html",
        latest_result=latest_result,
        records=records,
        error=None,
    )


@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@app.route("/processed/<path:filename>")
def processed(filename):
    return send_from_directory(PROCESSED_DIR, filename)


@app.route("/refresh")
def refresh():
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
