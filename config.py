import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Disable ChromaDB telemetry to prevent console log clutter
os.environ["ANON_TELEMETRY"] = "False"

# Ollama Cloud API Configuration
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "https://api.siliconflow.cn/v1")

# Best specialized models on SiliconFlow - optimized for reasoning depth and speed (free tier compatible)
MODEL_GUARDRAIL_AGENT    = "deepseek-ai/DeepSeek-V3"                 # High-speed factual gatekeeper
MODEL_RESEARCHER_AGENT   = "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B" # Deep reasoning distilled model for RAG & synthesis
MODEL_ANALYST_AGENT      = "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B" # Deep Socratic questioning & analysis
MODEL_RISK_ASSESSOR_AGENT= "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"
MODEL_RECOMMENDER_AGENT  = "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"
MODEL_REPORTER_AGENT     = "deepseek-ai/DeepSeek-V3"                 # Quick structured markdown reporter


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
