import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Disable ChromaDB telemetry to prevent console log clutter
os.environ["ANON_TELEMETRY"] = "False"

# Ollama Cloud API Configuration
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "https://ollama.com/v1")

# Best specialized models on Ollama Cloud - assigned by agent specialty & speed
MODEL_GUARDRAIL_AGENT    = "nemotron-3-nano:30b" # Fast factual gatekeeper
MODEL_PROFILER_AGENT     = "nemotron-3-nano:30b" # Fast reader profiler
MODEL_RECOMMENDER_AGENT  = "gpt-oss:20b"          # Fast factual search synthesizer
MODEL_ANALYST_AGENT      = "gemma4:31b"           # Deep Socratic questioning model
MODEL_RISK_ASSESSOR_AGENT= "nemotron-3-super"     # Deep cognitive blindspot critic
MODEL_REPORTER_AGENT     = "gemma4:31b"           # Structured Markdown & Mermaid reporter


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
