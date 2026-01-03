from contextlib import asynccontextmanager
import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.modules.loader import ModuleLoader
from app.modules.registry import ModuleRegistry


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load local and external plugins
    print("Loading modules...")
    ModuleLoader.load_modules("app.plugins.local")
    ModuleLoader.load_modules("app.plugins.external")
    
    # Initialize loaded modules and register routes
    for module in ModuleRegistry.get_all_modules():
        print(f"Initializing module: {module.metadata.name}")
        if await module.initialize():
            # Register module routes under /api/v1/modules/{module_name}
            app.include_router(
                module.router, 
                prefix=f"{settings.API_V1_STR}/modules/{module.metadata.name}", 
                tags=[f"Module: {module.metadata.name}"]
            )
            print(f"Routes registered for {module.metadata.name}")
    
    yield
    
    # Shutdown modules
    for module in ModuleRegistry.get_all_modules():
        await module.shutdown()


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
