# MarineXtract

MarineXtract is a web application that identifies marine algae species from an uploaded image and presents basic commercial information for the prediction.

The application uses a Flask backend and a PyTorch EfficientNetV2-S image-classification model. Predictions include the species name, common name, confidence score, estimated value in INR per kilogram, and listed commercial uses.

## Features

- Upload an algae image through a browser interface.
- Preview the selected image before prediction.
- Classify the image into one of seven configured algae species.
- Display prediction confidence and commercial metadata.
- Expose health, prediction, and species metadata API endpoints.
- Use CUDA automatically when available, with CPU fallback.

## Supported species

The bundled model is configured for:

1. *Caulerpa lentilifera* (Sea Grapes)
2. *Caulerpa sertularioides* (Green Caviar Seaweed)
3. *Kappaphycus* (Cottonii)
4. *Padina australis* (Peacock's Tail)
5. *Sargassum muticum* (Wireweed)
6. *Turbinaria australis* (Australian Turbinaria)
7. *Ulva lactuca* (Sea Lettuce)

## Project structure

```text
MarineXtract/
├── app.py                         # Flask application and API routes
├── marinextract_efficientnetv2.pth # Trained model checkpoint
├── requirements.txt               # Python dependencies
├── backend/
│   ├── metadata.py                # Species classes and commercial metadata
│   └── model_loader.py            # Model construction, loading, and inference
├── templates/
│   └── index.html                 # Web interface
└── static/
    ├── css/style.css              # Interface styling
    └── js/app.js                  # Upload, preview, and API interaction
```

## Requirements

- Python 3.10 or later
- pip
- The included `marinextract_efficientnetv2.pth` checkpoint
- Optional: a CUDA-capable PyTorch environment for GPU inference

## Installation

From the repository root, create and activate a virtual environment:

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Running the application

```bash
python app.py
```

The development server listens on `http://localhost:5000`. Open that URL in a browser, select an algae image, and choose **Predict species**.

The application loads the model during startup. Ensure the checkpoint remains at the repository root with the exact filename `marinextract_efficientnetv2.pth`.

## API

### Health check

```http
GET /api/health
```

Example response:

```json
{
  "status": "ok",
  "model": "MarineXtract EfficientNetV2-S"
}
```

### Predict a species

```http
POST /api/predict
Content-Type: multipart/form-data
```

The uploaded image must use the form field name `image`.

```bash
curl -X POST -F "image=@path/to/algae.jpg" http://localhost:5000/api/predict
```

The response contains `predicted_species`, `common_name`, `confidence`, `commercial_value_inr`, `price_per_kg_inr`, and `commercial_uses`.

### List species metadata

```http
GET /api/species
```

Returns the configured species list and its commercial metadata.

## Inference details

Uploaded images are converted to RGB, resized to `384 x 384`, converted to tensors, and normalized using ImageNet mean and standard deviation values. The model returns the class with the highest softmax probability.

Commercial values are static metadata configured in `backend/metadata.py`; they are estimates provided by the application and should not be treated as live market prices.

## Development notes

- The current entry point enables Flask debug mode. Disable debug mode and use a production WSGI server before deploying publicly.
- No automated test suite is currently included in the repository.
- The model checkpoint is required for startup and inference.
