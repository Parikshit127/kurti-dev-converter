"""
Web application for Unicode to Kruti Dev 010 converter.

Provides:
- File upload conversion (.doc / .docx)
- Direct text conversion (paste Unicode → get Kruti Dev)
- Health check endpoint
- Proper error handling and cleanup
"""

from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import shutil
import os
import uuid
import logging
import traceback
import tempfile
import gc
from core.converter import DocxConverter
from core.reorder import MangalToKrutiDevConverter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Constants
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15MB limit

# Setup
app = FastAPI(
    title="Unicode to KrutiDev Converter",
    description="Convert Hindi documents and text from Unicode (Mangal) to Kruti Dev 010",
    version="2.0.0",
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Use system temp directory
UPLOAD_DIR = os.environ.get(
    "UPLOAD_DIR",
    os.path.join(tempfile.gettempdir(), "fontchanger_uploads"),
)
try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    logger.info(f"Upload directory: {UPLOAD_DIR}")
except Exception as e:
    logger.error(f"Failed to create upload directory: {e}")
    UPLOAD_DIR = "/tmp/fontchanger_uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

# Templates
templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "ui", "templates")
)

# Mount static files
STATIC_DIR = os.path.join(BASE_DIR, "ui", "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Converters
docx_converter = None
text_converter = None
try:
    docx_converter = DocxConverter()
    text_converter = MangalToKrutiDevConverter()
    logger.info("Converters initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize converters: {e}")

# Favicon
FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" rx="15" fill="#6366f1"/>
  <text x="50" y="70" font-size="50" text-anchor="middle" fill="white" font-family="sans-serif" font-weight="bold">अ</text>
</svg>"""


# ---- Pydantic Models ----

class TextConvertRequest(BaseModel):
    text: str


class TextConvertResponse(BaseModel):
    converted: str
    original_length: int
    converted_length: int


# ---- Routes ----

@app.get("/favicon.ico")
async def favicon():
    return Response(content=FAVICON_SVG, media_type="image/svg+xml")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "docx_converter_ready": docx_converter is not None,
        "text_converter_ready": text_converter is not None,
        "version": "2.0.0",
    }


@app.post("/convert-text", response_model=TextConvertResponse)
async def convert_text(req: TextConvertRequest):
    """Convert plain text from Unicode to Kruti Dev."""
    if text_converter is None:
        raise HTTPException(status_code=500, detail="Text converter not initialized")

    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="No text provided")

    if len(req.text) > 100_000:
        raise HTTPException(status_code=400, detail="Text too long (max 100,000 characters)")

    try:
        converted = text_converter.convert(req.text)
        return TextConvertResponse(
            converted=converted,
            original_length=len(req.text),
            converted_length=len(converted),
        )
    except Exception as e:
        logger.error(f"Text conversion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")


@app.post("/convert")
async def convert_file(file: UploadFile = File(...)):
    """Convert a .doc / .docx file from Unicode to Kruti Dev."""
    logger.info(f"Received file for conversion: {file.filename}")

    if docx_converter is None:
        return JSONResponse(
            status_code=500,
            content={"error": "Document converter not initialized. Check server logs."},
        )

    filename_lower = (file.filename or "").lower()
    if not filename_lower.endswith((".docx", ".doc")):
        return JSONResponse(
            status_code=400,
            content={"error": "Only .doc and .docx files are supported"},
        )

    input_path = None
    output_path = None

    try:
        unique_id = str(uuid.uuid4())
        input_filename = f"{unique_id}_{file.filename}"
        input_path = os.path.join(UPLOAD_DIR, input_filename)

        logger.info(f"Saving uploaded file to: {input_path}")
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if not os.path.exists(input_path):
            raise Exception("Failed to save uploaded file")

        file_size = os.path.getsize(input_path)
        logger.info(f"File saved. Size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")

        if file_size > MAX_FILE_SIZE:
            raise Exception(
                f"File too large ({file_size / (1024*1024):.1f}MB). "
                f"Maximum: {MAX_FILE_SIZE / (1024*1024):.0f}MB"
            )

        gc.collect()

        base_name, _ = os.path.splitext(file.filename)
        output_filename = f"KrutiDev_{base_name}.docx"
        output_path = os.path.join(UPLOAD_DIR, output_filename)

        logger.info(f"Starting conversion. Output path: {output_path}")
        docx_converter.convert_file(input_path, output_path)

        gc.collect()

        if not os.path.exists(output_path):
            raise Exception("Conversion completed but output file not found")

        output_size = os.path.getsize(output_path)
        logger.info(f"Conversion successful. Output size: {output_size} bytes")

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Conversion failed: {error_msg}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        for path in [input_path, output_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass

        return JSONResponse(
            status_code=500,
            content={"error": f"Conversion failed: {error_msg}"},
        )
    finally:
        if input_path and os.path.exists(input_path):
            try:
                os.remove(input_path)
                logger.info("Cleaned up input file")
            except Exception as e:
                logger.warning(f"Failed to cleanup input file: {e}")

    return FileResponse(
        output_path,
        media_type=(
            "application/vnd.openxmlformats-officedocument"
            ".wordprocessingml.document"
        ),
        filename=output_filename,
        background=None,
    )
