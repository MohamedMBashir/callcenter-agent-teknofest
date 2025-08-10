import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class GroqSTT:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Provide api key")

        self.client = Groq(api_key=api_key)
        self.model = os.getenv('STT_MODEL')
        self.language = os.getenv('STT_LANGUAGE')
        print("STT initialized")

    def transcribe(self, file_path: str) -> str:
        """Transcribe audio file to text"""
        with open(file_path, "rb") as audio_file:
            result = self.client.audio.transcriptions.create(
                file=(file_path, audio_file.read()),
                model=self.model,
                language=self.language,
            )
        return result.text.strip()
