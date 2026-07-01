import sys
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

from rich.console import Console
console = Console()
from rich.text import Text

def print_header(title: str):
    """Print system startup header."""
    header_text = Text(title, style="bold cyan")
    separator = "═" * 70
    console.print()
    console.print(header_text)
    console.print(Text(separator, style="cyan"))
    console.print()

def print_separator():
    """Print standard section separator."""
    console.print(Text("━" * 70, style="dim white"))
    console.print()

def print_agent_start(agent_name: str, action: str):
    """Print agent start message."""
    icon_map = {
        "Guardrail Agent": "🛡️",
        "Researcher Agent": "🔍",
        "Analyst Agent": "📊",
        "Risk Assessor Agent": "⚠️",
        "Recommender Agent": "💡",
        "Reporter Agent": "📄"
    }
    icon = icon_map.get(agent_name, "🤖")
    console.print(Text(f"{icon} [{agent_name}] ", style="bold green") + Text(action, style="white"))

def print_agent_info(info_lines: list[str]):
    """Print details produced by an agent."""
    for line in info_lines:
        console.print(Text(f"   {line}", style="dim white"))

def print_agent_complete(agent_name: str, duration: float, tokens: int = 0):
    """Print agent completion stats."""
    console.print(Text(f"   ⏱ {duration:.1f}s", style="dim cyan") + Text(" | ", style="dim white") + Text(f"{tokens} tokens", style="dim magenta"))
    console.print()

def print_resolution_complete(summary_stats: dict):
    """Print execution end summary."""
    console.print(Text("✅ RESOLUTION COMPLETE", style="bold green"))
    console.print()
    console.print(Text("📊 Pipeline Summary:", style="bold white"))
    for key, value in summary_stats.items():
        console.print(Text(f"   {key}: ", style="bold cyan") + Text(str(value), style="white"))
    console.print()

def print_artifacts(artifacts: list[str]):
    """Print generated artifacts list."""
    console.print(Text("📄 Generated Artifacts:", style="bold white"))
    for art in artifacts:
        console.print(Text(f"   - {art}", style="dim green"))
    console.print()
