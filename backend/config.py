import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Flask Configuration
FLASK_ENV = os.getenv("FLASK_ENV", "development")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

# Validate required environment variables
def validate_config():
    """Validate that all required environment variables are set."""
    required_vars = {
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "FIRECRAWL_API_KEY": FIRECRAWL_API_KEY,
        "DATABASE_URL": DATABASE_URL,
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True