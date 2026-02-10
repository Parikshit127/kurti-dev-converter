# Unicode → KrutiDev 010 Converter

A production-grade web application that converts Hindi text and documents from **Unicode (Mangal)** to **KrutiDev 010** legacy font encoding.

## Features

- **📝 Real-time Text Conversion** — Paste Unicode Hindi text and get instant KrutiDev output
- **📄 Document Conversion** — Upload `.doc` / `.docx` files and download converted documents
- **🔤 Syllable-Aware Engine** — Linguistically accurate conversion with proper matra positioning, reph/rakar handling, and conjunct recognition
- **✅ Verified Accuracy** — All mappings verified against [unicodetokrutidev.net](https://unicodetokrutidev.net) reference converter
- **⚡ Fast & Lightweight** — No external APIs or AI keys required

## Conversion Accuracy

The converter handles:

| Feature | Examples |
|---|---|
| Independent Vowels | ए → `,` • ऐ → `,s` • आ → `vk` |
| Consonant + Matra | कि → `fd` (i-matra reordering) |
| Conjuncts | क्ष → `{k` • त्र → `=` • द्व → `}` |
| Reph (र्) | धर्म → `/keZ` • कर्म → `deZ` |
| Rakar (्र) | राष्ट्र → `jk"Vª` |
| Special Ri-Matra | कृ → `—` • दृ → `–` • हृ → `â` |
| Nukta Consonants | ड़ → `M+` • ढ़ → `<+` |
| Mixed Language | Hindi-English text handled seamlessly |

## Tech Stack

- **Backend:** Python, FastAPI, Gunicorn + Uvicorn
- **Document Processing:** python-docx
- **Frontend:** HTML, CSS, Vanilla JS
- **Deployment:** Render / Railway / Docker

## Quick Start (Local)

```bash
# Clone the repository
git clone https://github.com/Parikshit127/kurti-dev-converter.git
cd kurti-dev-converter

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

Open http://localhost:8000 in your browser.

## Running Tests

```bash
python -m pytest tests/ -v
```

## Deployment

### Render (Recommended)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Render will auto-detect the `render.yaml` configuration
5. Click **Deploy**

### Docker

```bash
docker build -t krutidev-converter .
docker run -p 8000:8000 krutidev-converter
```

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Web interface |
| `/health` | GET | Health check |
| `/convert-text` | POST | Convert text (JSON: `{"text": "..."}`) |
| `/convert` | POST | Convert .docx file (multipart form) |

## Project Structure

```
fontchanger/
├── core/
│   ├── converter.py    # DOCX file processing engine
│   ├── reorder.py      # Unicode → KrutiDev conversion logic
│   └── mappings.py     # Character mapping tables
├── ui/
│   ├── web_app.py      # FastAPI application
│   └── templates/
│       └── index.html  # Web interface
├── tests/
│   └── test_logic.py   # Comprehensive test suite (96 tests)
├── main.py             # Entry point
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment config
├── Procfile            # Process file for deployment
├── Dockerfile          # Docker configuration
└── README.md
```

## License

MIT
