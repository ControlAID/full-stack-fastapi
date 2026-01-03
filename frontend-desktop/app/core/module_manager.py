import os
import sys
import shutil
import zipfile
import subprocess
import requests
from pathlib import Path
from app.core.config import settings
from app.services.auth import AuthService

class ModuleManager:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
        self.plugins_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "plugins"
        
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(parents=True, exist_ok=True)

    def install_module(self, module_name: str) -> bool:
        """
        Download and install a module from the backend.
        """
        print(f"Installing module: {module_name}...")
        
        # 1. Download Zip
        url = f"{settings.API_URL}/modules/{module_name}/download"
        headers = self.auth_service.get_headers()
        
        try:
            response = requests.get(url, headers=headers, stream=True)
            if response.status_code != 200:
                print(f"Failed to download module. Status: {response.status_code}")
                return False
                
            # Save Zip temporarily
            zip_path = self.plugins_dir / f"{module_name}.zip"
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            # 2. Extract
            target_dir = self.plugins_dir / module_name
            if target_dir.exists():
                shutil.rmtree(target_dir)
            target_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
                
            # Cleanup Zip
            os.remove(zip_path)
            
            # 3. Install Dependencies
            self._install_dependencies(target_dir)
            
            print(f"Module {module_name} installed successfully.")
            return True
            
        except Exception as e:
            print(f"Error installing module {module_name}: {e}")
            return False

    def _install_dependencies(self, module_dir: Path):
        """
        Install dependencies from requirements.txt into the current environment.
        """
        req_file = module_dir / "requirements.txt"
        if req_file.exists():
            print(f"Installing dependencies for {module_dir.name}...")
            try:
                # Use the current python interpreter to install
                # NOTE: In a real production app, you might want to install to a local 'libs' folder
                # and add it to sys.path to avoid polluting the global user env.
                # For this controlled venv environment, installing to site-packages is acceptable.
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
                    stdout=subprocess.DEVNULL, # Suppress noisy output
                    stderr=subprocess.PIPE
                )
                print("Dependencies installed.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to install dependencies: {e}")
