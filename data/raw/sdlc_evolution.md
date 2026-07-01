# SDLC Evolution at FPT Software

## SDLC 1.0: Manual/Human-Only
Traditional waterfall methodology with:
- Months-long development cycles
- Manual requirements gathering and documentation
- Sequential handoffs between teams
- High rework rates due to late defect detection
- No AI assistance

## SDLC 2.0: Specialized Agents (Current — Partially Deployed)
Individual AI agents working independently:
- **CodeVista**: Handles coding tasks independently
- **AgentVista**: Handles design and architecture decisions independently
- **TestVista**: Handles testing tasks independently
- Each agent has limited context of what other agents are doing
- No feedback loops between agents (e.g., TestVista cannot tell CodeVista to fix a bug)
- **30% time savings** compared to SDLC 1.0
- **Limitation**: Information is lost at each handoff between phases

## SDLC 3.0: Multi-Agent Collaboration (THE GAP — Not Yet Implemented)
Same agent roles but with parallel processing and smarter orchestration:
- **Feedback loops**: Review Agent → Coding Agent → Review again until quality threshold met
- **Dynamic routing**: Supervisor decides next step based on quality metrics
- **Shared state**: All agents read/write to common state (requirement, code, review, tests)
- **RAG integration**: Agents retrieve enterprise knowledge before making decisions
- **Context preservation**: No information loss between SDLC phases
- **50% time savings** target compared to SDLC 1.0
- **This is the unsolved problem** — FPT's own presentations state this as the next frontier

## SDLC 4.0: Hyper Agents (Future Vision)
Fully autonomous, innovation-driving agents:
- Full-cycle autonomous execution
- Cross-project learning and knowledge accumulation
- Self-improving systems
- Human-on-the-loop (oversight only, not approval)
