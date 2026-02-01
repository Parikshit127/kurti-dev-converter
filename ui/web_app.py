
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import shutil
import os
import uuid
from core.converter import DocxConverter

# Setup
app = FastAPI(title="Unicode to KrutiDev Converter")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "temp_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "ui", "templates"))

# Converter
converter = DocxConverter()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/convert")
async def convert_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are supported")

    # Save Upload
    unique_id = str(uuid.uuid4())
    input_filename = f"{unique_id}_{file.filename}"
    input_path = os.path.join(UPLOAD_DIR, input_filename)
    
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Convert
    output_filename = f"KrutiDev_{file.filename}"
    output_path = os.path.join(UPLOAD_DIR, output_filename)
    
    try:
        converter.convert_file(input_path, output_path)
    except Exception as e:
        # Cleanup input
        if os.path.exists(input_path):
            os.remove(input_path)
        return {"error": str(e)}

    # Cleanup input
    if os.path.exists(input_path):
        os.remove(input_path)
        
    # Return File
    # Return File
    return FileResponse(
        output_path, 
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        filename=output_filename
    )

    # Note: Output file cleanup isn't handled here for simplicity of download. 
    # In a real app, use a background task to clean older files.
