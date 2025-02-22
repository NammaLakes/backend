import secrets
from lakewatch.settings import API_KEYS

def generate_api_key():
    return secrets.token_hex(32)

def validate_api_key(api_key: str) -> bool:
    return api_key in API_KEYS
