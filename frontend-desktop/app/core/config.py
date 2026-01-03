import os
from pydantic import BaseModel

class Settings(BaseModel):
    API_V1_STR: str = "/api/v1"
    SERVER_HOST: str = os.getenv("SERVER_HOST", "http://localhost:8000")
    
    @property
    def API_URL(self) -> str:
        return f"{self.SERVER_HOST}{self.API_V1_STR}"

settings = Settings()
