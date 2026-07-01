import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Disable ChromaDB telemetry to prevent console log clutter
os.environ["ANON_TELEMETRY"] = "False"

# Ollama Cloud API Configuration
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "https://ollama.com/v1")

# Best specialized models on Ollama Cloud — optimized for functional strengths and low latency (free tier compatible)
MODEL_GUARDRAIL_AGENT    = "meta-llama/llama-3.1-8b-instruct:free"     # High-speed instruction-following gatekeeper (free)
MODEL_RESEARCHER_AGENT   = "google/gemini-2.5-flash"   # Extremely fast factual synthesis and RAG context summary (free)
MODEL_ANALYST_AGENT      = "qwen3-coder-next"   # Extremely fast reasoning for trade-offs & complex evaluation matrix (free)
MODEL_RISK_ASSESSOR_AGENT= "qwen3-coder-next"   # Extremely fast reasoning for compliance & multi-dimensional risk matrix (free)
MODEL_RECOMMENDER_AGENT  = "qwen3-coder-next"   # Extremely fast strategic roadmap and KPI planner (free)
MODEL_REPORTER_AGENT     = "qwen3-coder-next"   # Code-specialized model for reports & syntax-valid Mermaid flowcharts (free)


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
OUTPUT_DIR = os.path.join(RUNNING_DIR, "output")
