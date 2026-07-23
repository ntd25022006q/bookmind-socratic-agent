import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Disable ChromaDB telemetry to prevent console log clutter
os.environ["ANON_TELEMETRY"] = "False"

# Ollama Cloud API Configuration
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "https://ollama.com/v1")

# Model lineup: deep reasoning models for high accuracy and relevance
MODEL_GUARDRAIL_AGENT    = "gemma4:12b"           # Fast + accurate gatekeeper
MODEL_PROFILER_AGENT     = "gemma4:27b"           # Deep reader profiling
MODEL_RECOMMENDER_AGENT  = "gemma4:27b"           # Factual VNU-LIC synthesis
MODEL_ANALYST_AGENT      = "gemma4:31b"           # Max deep Socratic reasoning
MODEL_RISK_ASSESSOR_AGENT= "gemma4:31b"           # Max deep cognitive blindspot critic
MODEL_REPORTER_AGENT     = "gemma4:31b"           # Max structured academic Markdown reporter


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
