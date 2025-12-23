import os
import shutil
import tempfile
from fastapi import UploadFile, HTTPException
from pdf2docx import Converter as PdfConverter
from moviepy import VideoFileClip, AudioFileClip

class ConverterService:
    def _save_upload_file(self, upload_file: UploadFile) -> str:
        try:
            # Create a unique temp file
            fd, path = tempfile.mkstemp()
            with os.fdopen(fd, 'wb') as tmp:
                shutil.copyfileobj(upload_file.file, tmp)
            return path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save upload file: {str(e)}")

    def convert_pdf_to_word(self, file_path: str) -> str:
        docx_path = file_path + ".docx"
        try:
            cv = PdfConverter(file_path)
            cv.convert(docx_path)
            cv.close()
            return docx_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF conversion failed: {str(e)}")

    def extract_audio(self, file_path: str) -> str:
        audio_path = file_path + ".mp3"
        try:
            # Load video file
            video = VideoFileClip(file_path)
            # Write audio
            video.audio.write_audiofile(audio_path, logger=None)
            video.close()
            return audio_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Audio extraction failed: {str(e)}")

    def video_to_gif(self, file_path: str) -> str:
        gif_path = file_path + ".gif"
        try:
            video = VideoFileClip(file_path)
            # Resize to reduce size, or keep original? Let's make it manageable
            # For utility, maybe limit to 10 seconds or resize?
            # Doing simple conversion for now.
            video.write_gif(gif_path, logger=None)
            video.close()
            return gif_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"GIF conversion failed: {str(e)}")

    def cleanup(self, *paths):
        for path in paths:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass

converter_service = ConverterService()
