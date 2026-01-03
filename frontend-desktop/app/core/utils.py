import uuid
import hashlib

def get_mac_address() -> str:
    """
    Returns the MAC address of the current machine.
    Formatted as XX:XX:XX:XX:XX:XX
    """
    mac_num = uuid.getnode()
    mac_hex = '{:012x}'.format(mac_num)
    mac_str = ":".join(mac_hex[i:i+2] for i in range(0, 12, 2))
    return mac_str.upper()

def get_machine_id() -> str:
    """
    Returns a unique hash for this machine based on MAC.
    Useful if we want to obscure the real MAC.
    """
    mac = get_mac_address()
    return hashlib.sha256(mac.encode()).hexdigest()
