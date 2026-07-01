# FPT Software AI Center — Research Projects

## AgileCoder: Dynamic Collaborative Agents for Software Development
- **Published**: FORGE 2025 (ICSE workshop)
- **Authors**: Minh Huynh Nguyen, Thang Chau Phan, Phong X. Nguyen, Nghi D. Q. Bui
- **GitHub**: https://github.com/FSoft-AI4Code/AgileCoder (459 stars, 59 forks)

### Architecture — 5 Agent Roles
| Agent | Role | Responsibility |
|-------|------|----------------|
| Product Manager (PM) | Requirements | Creates product backlog with tasks and acceptance criteria |
| Scrum Master (SM) | Coordination | Reviews backlog, initiates sprints, decides deliverability |
| Developer (Dev) | Implementation | Generates and refactors code, annotates with docstrings |
| Senior Developer (SD) | Quality | 3-step static review: basic errors, sprint alignment, acceptance + bugs |
| Tester | Verification | Generates test suites, creates testing plan, reports bugs |

### Key Innovation: Dynamic Code Graph Generator (DCGG)
- Maintains a Code Dependency Graph (CDG) — nodes are code files, edges are import relationships
- Updates dynamically as code changes
- Enables test case targeting and context-aware code retrieval
- Solves LLM context window problem by selective retrieval

### Results
- **HumanEval**: 70.53% pass@1 (GPT-3.5), 79.27% (Claude 3 Haiku)
- **MBPP**: 80.92% pass@1 (GPT-3.5), 84.31% (Claude 3 Haiku)
- Outperforms ChatDev and MetaGPT

### Limitations
- No RAG — relies entirely on LLM parametric knowledge
- No LangGraph — uses raw OpenAI API
- No human-in-the-loop governance
- No cross-project learning

---

## HyperAgent: Generalist Software Engineering Agents
- **Published**: arXiv 2409.16299 (September 2024)
- **Authors**: Huy Nhat Phan, Phong X. Nguyen, Nghi D. Q. Bui
- **GitHub**: https://github.com/FSoft-AI4Code/HyperAgent (243 stars, 27 forks)

### Architecture — 4 Specialized Agents
| Agent | Role | LLM Requirement |
|-------|------|----------------|
| Planner | Central decision-maker, processes task prompts, coordinates children | STRONG (Claude-3-Sonnet, GPT-4o) |
| Navigator | Codebase exploration, IDE-like navigation | LIGHTWEIGHT (Claude-3-Haiku) |
| Editor | Code modification and generation across files | STRONG (Claude-3-Sonnet) |
| Executor | Validates solutions, reproduces issues, runs tests | LIGHTWEIGHT |

### Communication
- Redis-based Message Queue for async communication
- Mixtral 8x7B summarizer reduces information loss between child→Planner

### Results
- **SWE-Bench-Verified**: 31.4% resolved rate
- **RepoExec**: 53.3% Pass@5
- **Defects4J**: 249 bugs fixed

### Limitations
- No RAG — no retrieval from documentation or knowledge bases
- No LangGraph — uses LangChain 0.2.x with custom Redis queue
- Fails on 69% of SWE-Bench issues — significant room for improvement

---

## Other Projects
- **CodeWiki** (ACL 2026, 1,170 stars): Holistic repository-level documentation
- **TestWeaver** (ICSE 2026): Execution-aware regression testing with LLMs
- **RepoHyper** (FORGE 2025, 73 stars): Graph-based end-to-end code completion
- **TheVault** (EMNLP 2023, 105 stars): Multilingual code dataset
