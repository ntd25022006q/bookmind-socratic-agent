# AI-First Challenges & Opportunities at FPT Software

## Strategic Context
FPT Corporation declared itself an "AI-First company" with three parallel transformations:
1. **Digital Transformation** — Modernizing legacy systems
2. **Intelligence Transformation** — Embedding AI across operations
3. **Green Transformation** — Sustainable tech practices

## Key Challenges

### 1. Context Overload Across Agents
Each agent (CodeVista, TestVista, AgentVista) operates with limited context. When they need to collaborate, there is no unified context-sharing mechanism. Information is lost at each handoff between SDLC phases.

### 2. Repository-Level Code Understanding
Existing tools "overly depend on LLMs for decision-making and managing code generation, proving inadequate for handling the complexity of entire software repositories" (AgileCoder paper). LLM context windows cannot fit entire codebases.

### 3. Cross-File Dependency Tracking
Changes in one file affect others. AgileCoder's DCGG solves this for single-agent code generation, but not for multi-agent coordination across SDLC phases where Planning, Coding, Review, and Testing agents all need awareness of dependencies.

### 4. Orchestration of Heterogeneous Agents
Different agents use different models, different tools, different context windows. No unified orchestration layer exists that can manage this diversity while maintaining coherent workflow.

### 5. Human-in-the-Loop Governance
Flezi Foundry requires human supervision, but current multi-agent systems do not have good mechanisms for selective human intervention. The challenge is determining when to involve humans vs. when to let agents work autonomously.

### 6. Knowledge Transfer Between SDLC Phases
Requirements from Planning → Design decisions from AgentVista → Code from CodeVista → Tests from TestVista — information is lost at each handoff. RAG (Retrieval Augmented Generation) can address this by providing persistent, searchable knowledge that any agent can access.

## Opportunities

### RAG as the Missing Link
RAG can address multiple challenges simultaneously:
- **Context preservation**: Knowledge base stores all decisions and artifacts
- **Cross-agent awareness**: Any agent can retrieve what other agents have produced
- **Enterprise knowledge integration**: Coding standards, past solutions, architecture decisions
- **Quality improvement**: Agents retrieve relevant standards before making decisions

### LangGraph as the Orchestration Layer
LangGraph provides:
- **StateGraph**: Shared state management across agents
- **Conditional edges**: Dynamic routing based on quality metrics
- **Feedback loops**: Cyclic graphs for iterative refinement
- **Visualization**: Graph structure is visible and debuggable
- **Checkpointing**: State persistence for recovery and replay

## FPT Software's AI Infrastructure
- 2 FPT AI Factories equipped with NVIDIA GPU H100 & H200
- Strategic partnerships: NVIDIA (AI infrastructure), Microsoft (Azure/collaboration)
- AI Talent Pipeline: 25,000+ AI-augmented globally certified engineers
- 2,000+ AI & Data Engineering students graduating annually from FPT Education Group
