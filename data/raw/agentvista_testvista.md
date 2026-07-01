# AgentVista & TestVista — FPT Software AI Agents

## AgentVista — Design & Maintenance Agent

### Overview
AgentVista is a reasoning agent that helps in design and maintenance decisions. It is part of the FleziPT platform's horizontal AI agents.

### Key Capabilities
- **Architecture design**: Can design initial architecture from requirements
- **Maintenance assistance**: Helps with system maintenance decisions
- **Reasoning**: Provides reasoning for design decisions
- **System understanding**: Analyzes existing system architecture

### Current Limitation
AgentVista is currently a standalone reasoning agent. In the SDLC 3.0 vision, it should collaborate with CodeVista and TestVista, but the multi-agent orchestration layer is still emerging. There is no direct communication between AgentVista and CodeVista for coordinated design-to-implementation workflows.

### SDLC Role
AgentVista handles the **Design and Maintenance** phases of the SDLC.

---

## TestVista — GenAI-Powered Testing Assistant

### Overview
TestVista is a GenAI-powered testing assistant that simplifies complex testing workflows and increases testing efficiency.

### Key Capabilities
- **Automated test generation**: Generates test cases from requirements and code
- **Test execution**: Runs tests and reports results
- **Integration validation**: Validates integration between components
- **Coverage analysis**: Identifies gaps in test coverage
- **Regression testing**: Detects regressions in existing functionality

### Current Limitation
TestVista functions independently. There is no feedback loop to CodeVista for iterative fix-test cycles. When a test fails, there is no automated mechanism to send the bug report back to CodeVista for fixing and then re-run the test. This manual handoff is a key gap that SDLC 3.0 aims to address.

### SDLC Role
TestVista handles the **Testing and Integration** phases of the SDLC.

---

## The Multi-Agent Gap
Both AgentVista and TestVista are standalone agents in SDLC 2.0. The multi-agent orchestration layer (SDLC 3.0) that enables:
- **Agent-to-agent communication**: Direct feedback between agents
- **Shared context**: Common understanding of project state
- **Dynamic routing**: Intelligent task routing based on quality metrics
- **Feedback loops**: Automated iteration cycles (code → test → fix → retest)

This is the frontier that FPT Software is working toward, and it represents a genuine research and engineering challenge.
