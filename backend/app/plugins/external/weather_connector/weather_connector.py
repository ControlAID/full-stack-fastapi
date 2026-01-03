from typing import Dict, Any
import httpx
import logging
from app.modules.base import BaseModule, ModuleMetadata

logger = logging.getLogger(__name__)

class WeatherConnectorModule(BaseModule):
    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            name="weather_connector",
            version="1.1.0",
            description="Conector externo real que consulta el clima vía wttr.in",
            author="ControlAI",
            license_required=False,
            is_external=True
        )
    
    async def initialize(self) -> bool:
        logger.info("Weather Connector Module v1.1.0 initialized")
        return True
    
    async def shutdown(self) -> bool:
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://wttr.in/?format=3", timeout=5.0)
                if response.status_code == 200:
                    return {"status": "ok", "api_connected": True}
        except Exception as e:
            return {"status": "degraded", "error": str(e)}
        return {"status": "error"}
    
    def register_routes(self):
        @self.router.get("/current")
        async def get_current_weather(city: str = "Medellin"):
            """
            Obtiene el clima real desde wttr.in (formato JSON).
            """
            try:
                # wttr.in/?format=j1 devuelve JSON detallado
                url = f"https://wttr.in/{city}?format=j1"
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=10.0)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Extraer lo más relevante
                    current = data.get("current_condition", [{}])[0]
                    return {
                        "city": city,
                        "temperature": current.get("temp_C"),
                        "condition": current.get("weatherDesc", [{}])[0].get("value"),
                        "humidity": current.get("humidity"),
                        "feels_like": current.get("FeelsLikeC"),
                        "source": "wttr.in (Real API)"
                    }
            except Exception as e:
                logger.error(f"Error fetching weather for {city}: {e}")
                return {
                    "error": "Could not fetch weather data",
                    "details": str(e),
                    "city": city,
                    "source": "Error"
                }
