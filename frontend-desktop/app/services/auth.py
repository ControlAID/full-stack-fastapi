import requests
import keyring
from typing import Optional
from app.core.config import settings

class AuthService:
    SERVICE_NAME = "ControlAI_Desktop"
    
    def __init__(self):
        self.token = self.load_token()

    def login(self, username, password) -> bool:
        """
        Authenticates against the backend and stores the token.
        """
        try:
            url = f"{settings.API_URL}/login/access-token"
            data = {
                "username": username,
                "password": password
            }
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                if access_token:
                    self.save_token(access_token)
                    return True
            return False
            
        except Exception as e:
            print(f"Login error: {e}")
            return False

    def save_token(self, token: str):
        self.token = token
        # Securely save token
        try:
            keyring.set_password(self.SERVICE_NAME, "access_token", token)
        except Exception as e:
            print(f"Error saving token to keyring: {e}")

    def load_token(self) -> Optional[str]:
        try:
            return keyring.get_password(self.SERVICE_NAME, "access_token")
        except Exception:
            return None

    def logout(self):
        self.token = None
        try:
            keyring.delete_password(self.SERVICE_NAME, "access_token")
        except Exception:
            pass

    def get_headers(self):
        """
        Return headers with Bearer token for API requests.
        """
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
