import os
from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from app.services.converters import converter_service

router = APIRouter(
    prefix="/api/convert",
    tags=["Converters"],
    responses={404: {"description": "Not found"}},
)

def remove_file(path: str):
    converter_service.cleanup(path)

@router.post("/pdf-to-word")
async def pdf_to_word(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Convert PDF to DOCX."""
    input_path = converter_service._save_upload_file(file)
    try:
        output_path = converter_service.convert_pdf_to_word(input_path)
        # Schedule cleanup
        background_tasks.add_task(remove_file, input_path)
        background_tasks.add_task(remove_file, output_path)
        return FileResponse(
            output_path, 
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
            filename=f"{file.filename}.docx"
        )
    except Exception:
        remove_file(input_path)
        raise

@router.post("/audio-extract")
async def audio_extract(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Extract Audio (MP3) from Video."""
    input_path = converter_service._save_upload_file(file)
    try:
        output_path = converter_service.extract_audio(input_path)
        background_tasks.add_task(remove_file, input_path)
        background_tasks.add_task(remove_file, output_path)
        return FileResponse(
            output_path,
            media_type="audio/mpeg",
            filename=f"{file.filename}.mp3"
        )
    except Exception:
        remove_file(input_path)
        raise

@router.post("/video-to-gif")
async def video_to_gif(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Convert Video to GIF."""
    input_path = converter_service._save_upload_file(file)
    try:
        output_path = converter_service.video_to_gif(input_path)
        background_tasks.add_task(remove_file, input_path)
        background_tasks.add_task(remove_file, output_path)
        return FileResponse(
            output_path,
            media_type="image/gif",
            filename=f"{file.filename}.gif"
        )
    except Exception:
        remove_file(input_path)
        raise
