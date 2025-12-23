# Personal Tools API

A collection of useful utility services built with FastAPI. This API provides tools for media downloading, image processing, earthquake data, and other common utilities.

## Features

### 1. BMKG Integration
Fetch the latest earthquake data from BMKG (Badan Meteorologi, Klimatologi, dan Geofisika).
- **Endpoint**: `GET /api/bmkg/autogempa`
- **Data Source**: BMKG Autogempa

### 2. Media Downloader
Download or get information from various media platforms (YouTube, TikTok, Instagram, X/Twitter, etc.) using `yt-dlp`.
- **Endpoints**:
    - `GET /api/dl/info`: Get metadata about the media.
    - `GET /api/dl/direct`: Get direct download links.

### 3. Image Tools
Utilities for image processing, including background removal.
- **Endpoints**:
    - `POST /api/img/remove-bg`: Upload an image to remove its background.
    - `GET /api/img/remove-bg-by-url`: Remove background from an image URL.
- **Note**: Requires `rembg` and `onnxruntime` installed (included in requirements).

### 4. Utilities
General helper tools.
- **Endpoints**:
    - `GET /api/utils/hash`: Generate hashes (MD5, SHA1, SHA256).
    - `GET /api/utils/base64/encode`: Base64 encode text.
    - `GET /api/utils/base64/decode`: Base64 decode text.
    - `GET /api/utils/qr`: Generate QR codes.

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd myapi
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the root directory to configure the application. You can copy the structure from `.env` (if available) or use the following defaults:

```env
API_KEY=CHANGE-ME
CORS_ALLOW_ORIGINS=*
BMKG_CACHE_TTL_SECONDS=30
YTDLP_CACHE_TTL_SECONDS=15
```

## Usage

1. **Run the server**
   ```bash
   uvicorn main:app --reload
   ```

2. **Access the API**
   The server will start at `http://127.0.0.1:8000`.

3. **API Documentation**
   Visit `http://127.0.0.1:8000/docs` for the interactive Swagger UI documentation.

## Authentication

All API endpoints are protected by an API Key. You must include the `x-api-key` header in your requests.

```http
GET /api/bmkg/autogempa HTTP/1.1
Host: 127.0.0.1:8000
x-api-key: CHANGE-ME
```
