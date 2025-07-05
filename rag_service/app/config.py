from dotenv import load_dotenv
import os

load_dotenv(override=True)

def get_env_var(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(f"Missing required env var: {key}")
    return val

MODEL_SERVICE_URL = get_env_var("MODEL_SERVICE_URL")
