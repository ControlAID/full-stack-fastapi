from typing import Dict, Any
import httpx
from app.modules.base import BaseModule, ModuleMetadata

class WeatherConnectorModule(BaseModule):
    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            name="weather_connector",
            version="1.0.0",
            description="Conector externo para servicios meteorológicos",
            author="ControlAI",
            license_required=False,
            is_external=True
        )
    
    async def initialize(self) -> bool:
        print("Weather Connector Module initialized")
        return True
    
    async def shutdown(self) -> bool:
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        # Simular chequeo de API externa
        return {"status": "ok", "api_connected": True}
    
    def register_routes(self):
        @self.router.get("/current")
        async def get_current_weather(city: str = "Medellin"):
            """
            Simula la obtención de clima desde una API externa.
            """
            # En un caso real, usaríamos httpx para llamar a OpenWeather u otro
            return {
                "city": city,
                "temperature": 24,
                "condition": "Cloudy",
                "source": "Mock External API"
            }
