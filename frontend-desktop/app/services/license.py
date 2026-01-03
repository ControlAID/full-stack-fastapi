import requests
from app.core.config import settings
from app.core.utils import get_mac_address
from app.services.auth import AuthService

class LicenseService:
    def __init__(self, auth_service: AuthService):
        self.auth = auth_service
        self.mac_address = get_mac_address()

    def check_binding(self) -> dict:
        """
        Checks if the current machine (MAC) is registered as an Access Point
        in the user's organization.
        
        Returns:
            dict: {"bound": bool, "access_point": dict | None, "message": str}
        """
        if not self.auth.token:
            return {"bound": False, "access_point": None, "message": "No authenticated"}

        url = f"{settings.API_URL}/access-points/"
        headers = self.auth.get_headers()
        params = {"device_id": self.mac_address}

        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    # Found matching AP
                    return {"bound": True, "access_point": data[0], "message": "Device bound"}
                else:
                    return {"bound": False, "access_point": None, "message": "Device not found in registry"}
            elif response.status_code == 403:
                return {"bound": False, "access_point": None, "message": "Permission denied (License/Role)"}
            else:
                return {"bound": False, "access_point": None, "message": f"Server error: {response.status_code}"}
                
        except Exception as e:
            return {"bound": False, "access_point": None, "message": f"Connection error: {e}"}

    def register_device(self, name: str, location: str) -> bool:
        """
        Registers the current device as a new Access Point.
        This usually requires Admin privileges in the Organization.
        """
        # First we need to know the organization ID... 
        # Ideally the backend handles this or we fetch current user info first.
        # But AccessPointCreate requires organization_id.
        # Let's assume we can fetch user profile first.
        
        # 1. Get User Profile to find Organization ID
        user_url = f"{settings.API_URL}/users/me"
        headers = self.auth.get_headers()
        
        try:
            user_resp = requests.get(user_url, headers=headers)
            if user_resp.status_code != 200:
                print(f"Failed to fetch user: {user_resp.text}")
                return False
                
            user_data = user_resp.json()
            org_id = user_data.get("organization_id")
            
            if not org_id:
                print("User has no organization")
                return False
                
            # 2. Register Access Point
            ap_url = f"{settings.API_URL}/access-points/"
            payload = {
                "name": name,
                "location": location,
                "device_id": self.mac_address,
                "organization_id": org_id,
                "enabled_modules": []
            }
            
            reg_resp = requests.post(ap_url, headers=headers, json=payload)
            if reg_resp.status_code == 200:
                return True
            else:
                print(f"Registration failed: {reg_resp.text}")
                return False
                
        except Exception as e:
            print(f"Error registering device: {e}")
            return False
