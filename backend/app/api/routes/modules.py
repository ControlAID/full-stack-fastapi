import shutil
import os
import io
import zipfile
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings

router = APIRouter(prefix="/modules", tags=["modules"])

@router.get("/{module_name}/download")
def download_module(module_name: str, current_user: CurrentUser):
    """
    Download the client-side package for a module as a Zip file.
    Only allows downloading modules that exist in plugins/local or plugins/external.
    """
    from pathlib import Path
    # 1. Locate the module directory
    # Calculate base path relative to this file
    # this file: /app/app/api/routes/modules.py
    # target: /app/app/plugins
    
    current_file = Path(__file__).resolve()
    # Go up 3 levels: routes -> api -> app -> (root of app package)
    app_dir = current_file.parent.parent.parent
    base_path = app_dir / "plugins"
    
    local_path = base_path / "local" / module_name / "client"
    external_path = base_path / "external" / module_name / "client"
    
    target_path = None
    if local_path.exists() and local_path.is_dir():
        target_path = local_path
    elif external_path.exists() and external_path.is_dir():
        target_path = external_path
        
    if not target_path:
        raise HTTPException(status_code=404, detail=f"Module '{module_name}' client package not found")
        
    # 2. Check License (Optional but recommended)
    # TODO: Verify if current_user.organization has access to this module via License
    
    # 3. Create Zip in memory
    io_stream = io.BytesIO()
    with zipfile.ZipFile(io_stream, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(target_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Calculate relative path for zip (e.g. module.py, requirements.txt)
                relative_path = os.path.relpath(file_path, target_path)
                zip_file.write(file_path, relative_path)
                
    io_stream.seek(0)
    
    headers = {
        'Content-Disposition': f'attachment; filename="{module_name}.zip"'
    }
    
    return StreamingResponse(io_stream, media_type="application/zip", headers=headers)
