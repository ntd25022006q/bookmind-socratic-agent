import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Disable ChromaDB telemetry to prevent console log clutter
os.environ["ANON_TELEMETRY"] = "False"

# Ollama Cloud API Configuration
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "https://ollama.com/v1")

# Best specialized models on Ollama Cloud - optimized for reasoning depth and speed (free tier compatible)
MODEL_GUARDRAIL_AGENT    = "minimax-m2.5"        # Factual gatekeeper
MODEL_RESEARCHER_AGENT   = "minimax-m2.5"        # Deep reasoning model for RAG & synthesis
MODEL_ANALYST_AGENT      = "minimax-m2.5"        # Deep Socratic questioning & analysis
MODEL_RISK_ASSESSOR_AGENT= "minimax-m2.5"
MODEL_RECOMMENDER_AGENT  = "minimax-m2.5"
MODEL_REPORTER_AGENT     = "minimax-m2.5"        # Quick structured markdown reporter


import sys

# Check if running in a PyInstaller bundle
if getattr(sys, 'frozen', False):
    # sys._MEIPASS contains the bundled files
    WORKSPACE_DIR = sys._MEIPASS
    RUNNING_DIR = os.path.dirname(sys.executable)
else:
    WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
    RUNNING_DIR = WORKSPACE_DIR

DATA_DIR = os.path.join(RUNNING_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
CHROMA_DB_DIR = os.path.join(DATA_DIR, "chroma_db")
# Use /tmp on cloud platforms (Render, Vercel) where the app dir may be read-only
if "RENDER" in os.environ or "VERCEL" in os.environ:
    OUTPUT_DIR = "/tmp"
else:
    OUTPUT_DIR = os.path.join(RUNNING_DIR, "output")
