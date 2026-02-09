from openai import OpenAI
import os
from pathlib import Path
from typing import Dict, Optional
from app.config import settings


class STTService:
    def __init__(self):
        self.client = None
        self.model_name = settings.WHISPER_MODEL
        
    def load_model(self):
        if self.client is None:
            print(f"Initializing OpenAI client with model: {self.model_name}")
            self.client = OpxenAI(api_key=settings.OPENAI_API_KEY)
            print("OpenAI client initialized successfully")
    
    async def transcribe_audio(
        self, 
        file_path: str, 
        language: Optional[str] = "ko",
        task: str = "transcribe"
    ) -> Dict:
        try:
            if self.client is None:
                self.load_model()
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Audio file not found: {file_path}")
            
            # OpenAI Whisper API 호출
            with open(file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=self.model_name,
                    file=audio_file,
                    language=language if language != "auto" else None,
                    response_format="verbose_json"
                )
            
            return {
                "text": response.text.strip(),
                "language": getattr(response, "language", language),
                "segments": getattr(response, "segments", []),
                "duration": getattr(response, "duration", 0)
            }
            
        except Exception as e:
            raise Exception(f"STT processing failed: {str(e)}")
    
    def cleanup_file(self, file_path: str):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Failed to remove file {file_path}: {e}")

# singleton instance
# 하나만 생성 되어야 해요잉
stt_service = STTService()
