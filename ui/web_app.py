
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import shutil
import os
import uuid
import logging
import traceback
import tempfile
from core.converter import DocxConverter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup
app = FastAPI(title="Unicode to KrutiDev Converter")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Use system temp directory for Railway compatibility (ephemeral filesystem)
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", os.path.join(tempfile.gettempdir(), "fontchanger_uploads"))
try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    logger.info(f"Upload directory created/verified: {UPLOAD_DIR}")
except Exception as e:
    logger.error(f"Failed to create upload directory: {e}")
    # Fallback to /tmp which should always work
    UPLOAD_DIR = "/tmp/fontchanger_uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

# Templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "ui", "templates"))

# Mount static files
STATIC_DIR = os.path.join(BASE_DIR, "ui", "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Converter - initialize lazily to catch any import errors
converter = None
try:
    converter = DocxConverter()
    logger.info("DocxConverter initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize DocxConverter: {e}")

# Favicon - inline SVG to prevent 404 errors
FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" rx="15" fill="#6366f1"/>
  <text x="50" y="70" font-size="50" text-anchor="middle" fill="white" font-family="sans-serif" font-weight="bold">अ</text>
</svg>"""

@app.get("/favicon.ico")
async def favicon():
    return Response(content=FAVICON_SVG, media_type="image/svg+xml")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway."""
    return {"status": "healthy", "converter_ready": converter is not None}

@app.post("/convert")
async def convert_file(file: UploadFile = File(...)):
    logger.info(f"Received file for conversion: {file.filename}")
    
    # Check if converter is initialized
    if converter is None:
        logger.error("Converter not initialized")
        return JSONResponse(
            status_code=500,
            content={"error": "Converter not initialized. Please check server logs."}
        )
    
    if not file.filename.endswith(".docx"):
        logger.warning(f"Invalid file type: {file.filename}")
        return JSONResponse(
            status_code=400,
            content={"error": "Only .docx files are supported"}
        )

    input_path = None
    output_path = None
    
    try:
        # Save Upload
        unique_id = str(uuid.uuid4())
        input_filename = f"{unique_id}_{file.filename}"
        input_path = os.path.join(UPLOAD_DIR, input_filename)
        
        logger.info(f"Saving uploaded file to: {input_path}")
        
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Verify file was saved
        if not os.path.exists(input_path):
            raise Exception("Failed to save uploaded file")
        
        file_size = os.path.getsize(input_path)
        logger.info(f"File saved successfully. Size: {file_size} bytes")

        # Convert
        output_filename = f"KrutiDev_{file.filename}"
        output_path = os.path.join(UPLOAD_DIR, output_filename)
        
        logger.info(f"Starting conversion. Output path: {output_path}")
        converter.convert_file(input_path, output_path)
        
        # Verify output was created
        if not os.path.exists(output_path):
            raise Exception("Conversion completed but output file not found")
        
        output_size = os.path.getsize(output_path)
        logger.info(f"Conversion successful. Output size: {output_size} bytes")

    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        logger.error(f"Conversion failed: {error_msg}")
        logger.error(f"Traceback: {error_trace}")
        
        # Cleanup on error
        if input_path and os.path.exists(input_path):
            try:
                os.remove(input_path)
            except:
                pass
        if output_path and os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass
        
        return JSONResponse(
            status_code=500,
            content={"error": f"Conversion failed: {error_msg}"}
        )
    
    finally:
        # Always cleanup input file
        if input_path and os.path.exists(input_path):
            try:
                os.remove(input_path)
                logger.info("Cleaned up input file")
            except Exception as e:
                logger.warning(f"Failed to cleanup input file: {e}")
        
    # Return File
    return FileResponse(
        output_path, 
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        filename=output_filename,
        background=None  # Don't use background task for Railway compatibility
    )

    # Note: Output file cleanup isn't handled here for simplicity of download. 
    # In a real app, use a background task to clean older files.
