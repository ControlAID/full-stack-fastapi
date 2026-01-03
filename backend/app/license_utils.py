import random
import string

def generate_license_key() -> str:
    """
    Generate a unique license key in the format XXXX-XXXX-XXXX-XXXX.
    """
    def generate_part(length: int = 4) -> str:
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

    return f"{generate_part()}-{generate_part()}-{generate_part()}-{generate_part()}"
