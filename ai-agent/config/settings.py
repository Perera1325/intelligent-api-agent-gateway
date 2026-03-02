import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    API_KEY = os.getenv("API_KEY", "vinod-secure-key")
    CACHE_TTL = int(os.getenv("CACHE_TTL", 60))
    FAILURE_THRESHOLD = 3
    COOLDOWN_TIME = 30
    RATE_LIMIT = 20
    RATE_WINDOW = 60