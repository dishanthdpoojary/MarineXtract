import io
import os

from flask import Flask, jsonify, render_template, request
from PIL import Image

from backend.model_loader import model_service

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health_check():
    return jsonify({"status": "ok", "model": "MarineXtract EfficientNetV2-S"})


@app.route("/api/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image file uploaded"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    try:
        image = Image.open(io.BytesIO(file.read())).convert("RGB")
        result = model_service.predict(image)
        return jsonify(result)
    except Exception as exc:  # pragma: no cover - defensive for UI errors
        return jsonify({"error": f"Prediction failed: {str(exc)}"}), 500


@app.route("/api/species")
def species_metadata():
    from backend.metadata import SPECIES_CLASSES

    return jsonify({"species": SPECIES_CLASSES})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
