import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY')
    ZENROWS_KEY = os.getenv('ZENROWS_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

