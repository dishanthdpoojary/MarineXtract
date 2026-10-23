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

For local use, simply run:

```powershell
python app.py
```

If sign-in has not been configured, the terminal prompts for a username and a
password (at least 12 characters) before starting the server. Password characters
are hidden while typing. The password hash and a stable session secret are saved
in `instance/login.json`, which is excluded from Git. Subsequent starts reuse
these settings, including when you start from a different terminal.

To configure or reset the local login separately, run `python setup_login.py`,
then restart the server and refresh the browser. Resetting rotates the session
secret and signs out existing local sessions. Keep `instance/` private.

For deployment, environment variables can override the saved local account.
Configure the workspace account in the same PowerShell session before starting:

```powershell
$env:MARINEXTRACT_USERNAME = "admin"
$env:MARINEXTRACT_PASSWORD = "choose-a-strong-password"
$env:MARINEXTRACT_SECRET_KEY = (python -c "import secrets; print(secrets.token_hex(32))")
python app.py
```

Keep the secret key stable across application processes and restarts if sessions
should remain valid. For other shells, set the same environment variables using
the shell's environment-variable syntax. There is no built-in password; sign-in
is disabled until a local login is saved or `MARINEXTRACT_PASSWORD` is set.
The username defaults to `admin`.
This is a single shared workspace account; registration and password recovery
are not included. Set `MARINEXTRACT_COOKIE_SECURE=1` when serving over HTTPS.

After configuring the environment, subsequent starts use:

```bash
python app.py
```

The development server listens on `http://localhost:5000`. Open that URL, sign in,
select an algae image, and choose **Predict species**. Sessions expire after eight
hours. Use **Sign out** to end a session.

The application loads the model on the first prediction and reuses it for later
requests. The login and analysis pages can load without waiting for PyTorch or
the checkpoint. The first prediction may take longer while the model initializes.
Keep the checkpoint at the repository root with the exact filename
`marinextract_efficientnetv2.pth`.

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

Prediction and species endpoints require a signed-in session. Prediction POSTs
also require the CSRF token from the analysis page's `csrf-token` meta tag in the
`X-CSRF-Token` header. The curl example below illustrates only the upload format;
an authenticated client must additionally send its session cookie and CSRF token.

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

- Debug mode is off by default and the automatic reloader is disabled. Set
  `MARINEXTRACT_DEBUG=1` only for local debugging. Use a production WSGI server
  before deploying publicly.
- Run authentication tests with `python -m unittest discover -s tests -v`.
  These checks mock the model loader and do not validate model inference.
- The model checkpoint is required for startup and inference.
