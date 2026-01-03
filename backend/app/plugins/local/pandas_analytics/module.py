from app.modules.base import BaseModule, ModuleMetadata

class PandasAnalytics(BaseModule):
    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            name="pandas_analytics",
            version="1.0.0",
            description="Analytics module using Pandas",
            author="ControlAI",
            license_required=True,
            is_external=False
        )
    
    async def initialize(self) -> bool:
        return True
    
    async def shutdown(self) -> bool:
        return True
