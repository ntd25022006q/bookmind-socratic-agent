import time
import os
import sys
import argparse

# Reconfigure stdout and stderr to use UTF-8 encoding to prevent UnicodeEncodeError on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from rich.console import Console
from src.utils.display import (
    print_header,
    print_separator,
    print_resolution_complete,
    print_artifacts
)
from src.state import ResearchState
from src.graph import app
from config import OUTPUT_DIR

console = Console()

def run_pipeline(topic: str):
    """Run the multi-agent research & analysis pipeline."""
    console.print(f"\n[bold green]📥 Starting Multi-Agent Research on Topic:[/]\n[italic white]\"{topic}\"[/]\n")
    print_separator()
    
    # Setup initial state
    initial_state: ResearchState = {
        "topic": topic,
        "research_data": "",
        "analysis": "",
        "risks": "",
        "recommendations": "",
        "report": "",
        "messages": [],
        "irrelevant": False,
        "csv_data": "",
        "retrieved_context": "",
        "citations": [],
        "query_type": "consulting",
        "language": "vi"
    }
    
    start_time = time.time()
    
    try:
        # Invoke LangGraph StateGraph asynchronously
        import asyncio
        final_state = asyncio.run(app.ainvoke(initial_state))
        total_duration = time.time() - start_time
        
        # Extract token counts
        total_tokens = 0
        for msg in final_state.get("messages", []):
            if hasattr(msg, "usage_metadata") and msg.usage_metadata:
                total_tokens += msg.usage_metadata.get("total_tokens", 0)
            elif hasattr(msg, "response_metadata") and "token_usage" in msg.response_metadata:
                total_tokens += msg.response_metadata.get("token_usage", {}).get("total_tokens", 0)
                
        # Generate final markdown report path
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        report_path = os.path.join(OUTPUT_DIR, "research_report.md")
        
        final_report = final_state.get("report", "# No report generated")
        from src.utils.cleaner import clean_internal_filenames
        final_report = clean_internal_filenames(final_report)
            
        # Save clean report without metrics suffix
        agents_count = 1 if final_state.get("irrelevant") else (3 if final_state.get("query_type") == "qa" else 6)
        metadata_suffix = f"""

---

### Executive Platform Metadata
*   **Pipeline Execution Time:** {total_duration:.2f}s
*   **Total Model Tokens Processed:** {total_tokens:,} tokens
*   **Total Coordinated Agents:** {agents_count}
"""
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(final_report)
            
        # Write metadata separately to avoid polluting the consulting report
        metadata_path = os.path.join(OUTPUT_DIR, "metadata.txt")
        with open(metadata_path, "w", encoding="utf-8") as f:
            f.write(metadata_suffix)
            
        # Print summary metrics
        summary_stats = {
            "Total agents": agents_count,
            "Execution time": f"{total_duration:.1f}s",
            "Total tokens": f"{total_tokens:,}",
            "Status": "COMPLETED SUCCESS ✅"
        }
        
        print_separator()
        print_resolution_complete(summary_stats)
        
        # Print artifacts paths
        artifacts_paths = [
            f"Compiled Report: output/research_report.md"
        ]
        print_artifacts(artifacts_paths)
        
    except Exception as e:
        console.print(f"[bold red]❌ Pipeline execution failed with error: {str(e)}")
        console.print_exception()
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="VNU BookMind Socratic Agentic Research Pipeline")
    parser.add_argument("--demo", action="store_true", help="Run the primary demo topic ('Should we switch to microservices?')")
    parser.add_argument("--topic", type=str, help="Custom research topic or question")
    parser.add_argument("--server", action="store_true", help="Start the FastAPI dashboard web server")
    
    args = parser.parse_args()
    
    print_header("🚀 VNU BookMind Socratic Agentic Research Suite")
    
    if args.server:
        import uvicorn
        
        # Read PORT and HOST from env dynamically for compatibility with Render/Cloud hosting
        host = os.environ.get("HOST", "0.0.0.0")
        port = int(os.environ.get("PORT", 8000))
        console.print(f"[bold green]Starting Dashboard Server on http://{host}:{port}...[/]")
        uvicorn.run("server:app", host=host, port=port, reload=False)
    elif args.demo:
        run_pipeline("Should we switch to microservices?")
    elif args.topic:
        run_pipeline(args.topic)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
