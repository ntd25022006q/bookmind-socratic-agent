# CodeVista — AI-Powered Coding Assistant

## Overview
CodeVista is FPT Software's AI-powered coding assistant, part of the FleziPT platform. It operates as a multi-agent system integrated into the IDE.

## Key Capabilities
- **Secure code generation**: Generates code inside IDE with enterprise-grade security
- **Real-time knowledge**: Provides contextual suggestions based on project context
- **Contextual code suggestions**: Understands file-level, codebase-level, and project-level context
- **Documentation generation**: Auto-generates docs at file, codebase, and project level
- **Reverse engineering**: Understands and documents existing code
- **Automated maintenance**: Suggests and implements code maintenance tasks
- **Bug fixing**: Identifies and fixes bugs with context-aware suggestions
- **Code refactoring**: Improves code quality while preserving behavior

## Performance Metrics
- Cuts development time by **60%**
- Speeds up sprints by **80%**
- Catches bugs **30% earlier** in the development cycle
- Increases code reuse by **10x**

## Current Limitation (SDLC 2.0)
CodeVista currently operates as a **single-agent coding assistant**. It does NOT coordinate with other agents (AgentVista, TestVista). There is no multi-agent orchestration layer that enables:
- Feedback loops from TestVista to CodeVista for iterative bug fixing
- Context sharing with AgentVista for architecture-aware code generation
- Collaborative decision-making across SDLC phases

## SDLC Role
CodeVista handles the **Planning, Analysis, and Implementation** phases of the SDLC.
