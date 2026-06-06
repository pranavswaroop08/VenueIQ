"""Configuration management for VenueIQ.

Handles environment variables and configuration with secure defaults.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Elasticsearch Configuration
ES_HOST = os.getenv("ES_HOST", "https://localhost:9200")
ES_USER = os.getenv("ES_USER", "elastic")
ES_PASSWORD = os.getenv("ES_PASSWORD", "")
ES_VERIFY_CERTS = os.getenv("ES_VERIFY_CERTS", "False").lower() == "true"

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Application Configuration
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def get_es_config():
    """Get Elasticsearch client configuration."""
    return {
        "hosts": [ES_HOST],
        "basic_auth": (ES_USER, ES_PASSWORD),
        "verify_certs": ES_VERIFY_CERTS,
    }
