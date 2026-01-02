---
id: 001
title: Advanced Phase Constitution Creation
stage: constitution
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5
feature: none
branch: master
user: architect
command: /sp.constitution
labels: ["constitution", "hackathon-ii", "spec-driven-development", "advanced-phase", "recurring-tasks", "due-dates", "reminders", "ai-readiness", "cloud-readiness"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - None (constitution document, no tests required)
---

## Prompt

You are a principal software architect (40+ years experience) specializing in:

Spec-Driven Development

AI-Native Systems

Cloud-Native Architectures

Hackathon-grade engineering rigor

Your task is to generate a Markdown sp.constitution file for the Advanced Phase of a Todo Application.

This constitution will govern all future Specs and implementations for this phase.

🧭 Hackathon Context (NON-NEGOTIABLE)

Hackathon: Hackathon II – Spec-Driven Development

Mandatory Rules:

Every feature must have:

A Markdown Constitution

A Markdown Spec

No manual coding allowed

All code must be generated using Claude Code

Specs must be iteratively refined until Claude Code generates the correct behavior

The Constitution is the highest authority

🧩 Project Evolution Context

This Todo App evolves across phases:

Phase I: In-memory Python CLI app

Phase II: Spec-Driven refinement

Phase III–V:

Integrated AI Chatbot

Cloud-native deployment (Minikube → DOKS)

OpenAI Chatkit

OpenAI Agents SDK

Official MCP SDK

The Constitution you generate must not conflict with future phases.

🚀 Phase Scope: ADVANCED FEATURES

The Constitution must explicitly govern Advanced-Level Intelligent Features only:

1. Recurring Tasks

Tasks can repeat (daily, weekly, monthly, custom)

Auto-rescheduling after completion

Rule-based recurrence (not hardcoded)

2. Due Dates & Time Reminders

Tasks may include:

Due date

Due time

Reminder logic must be deterministic

Architecture must allow:

Console notifications (Phase I–II)

Browser/system notifications (future phases)

🧠 Core Engineering Principles

The Constitution must define and enforce:

Spec-first development (spec precedes code)

Deterministic behavior

Explicit state transitions

Time-aware logic correctness

Human-language compatibility (future AI control)

Extensibility without refactoring core rules

📐 Constitutional Sections (MANDATORY)

Your output MUST include the following sections:

Purpose & Authority

Scope of This Constitution

Non-Negotiable Development Rules

Feature Governance

Recurring Tasks

Due Dates

Reminders

Temporal Logic Standards

State & Lifecycle Rules

AI-Readiness Guarantees

Cloud-Readiness Guarantees

Forbidden Practices

Success Criteria

⛔ Hard Constraints

The Constitution must clearly state:

No manual code writing

No speculative behavior

No hidden state

No time-based side effects without explicit spec

No coupling to UI, platform, or infrastructure

🧠 AI-Native Forward Compatibility

Even though this phase is not fully AI-driven yet, the Constitution must ensure:

All features can be controlled via natural language

Every action maps to an intent

Deterministic execution from conversational commands

Compatibility with:

OpenAI Chatkit

OpenAI Agents SDK

Official MCP SDK

📝 Output Rules

Output ONLY the Markdown sp.constitution

No explanations

No code

No examples

Use precise, formal, constitutional language

Keep tone authoritative and declarative

## Response snapshot

Generated comprehensive Advanced Phase Todo Application Constitution v1.0.0 governing:

**Core Principles (7 Non-Negotiable Rules):**
I. Spec-First Development - All code generated from approved Markdown specs
II. Deterministic Behavior - Reproducible outcomes, testable temporal logic
III. Explicit State Transitions - Documented lifecycle (pending→active→completed→snoozed)
IV. Time-Aware Logic Correctness - UTC storage, timezone-neutral, edge case handling
V. Human-Language Compatibility - Intent mapping for future AI control
VI. Extensibility Without Refactoring - Data-driven rules, plugin-ready architecture
VII. No Manual Coding - Claude Code-only generation (Hackathon II requirement)

**Feature Governance:**
- Recurring Tasks: Daily/weekly/monthly patterns, auto-rescheduling, rule-based (not hardcoded)
- Due Dates: Optional YYYY-MM-DD or ISO 8601 datetime, overdue detection
- Reminders: Absolute/relative times, multi-reminder support, platform-agnostic delivery

**Forward Compatibility Guarantees:**
- AI-Readiness: Natural language intent mapping, conversational examples
- Cloud-Readiness: Stateless design, API-first thinking, event-driven architecture
- Notification abstraction: Console (Phase II) → Browser/system (Phase III-V)

**Governance:**
- Semantic versioning (1.0.0)
- Amendment process requires ADR + approval
- Compliance checkpoints at spec/implementation/testing phases

File created: `.specify/memory/constitution.md` (445 lines)

## Outcome

- ✅ Impact: Established supreme governing document for Hackathon II Advanced Phase; defines immutable architectural/behavioral/process requirements for recurring tasks, due dates, and reminders with AI/cloud forward compatibility
- 🧪 Tests: N/A (constitutional document; validation occurs during spec/implementation compliance review)
- 📁 Files: Created `.specify/memory/constitution.md` (1 file, version 1.0.0)
- 🔁 Next prompts: 1) Template validation (verify plan/spec/tasks templates align with constitutional principles), 2) Feature specification creation (recurring tasks, due dates, reminders), 3) ADR for architectural decisions during planning
- 🧠 Reflection: Constitution successfully balances strict governance (no manual coding, deterministic behavior) with flexibility (data-driven rules, extensibility). Temporal logic standards and AI-readiness guarantees position project for seamless evolution through Phases III-V without refactoring. Next critical step: validate templates enforce constitutional compliance.

## Evaluation notes (flywheel)

- Failure modes observed: None (initial constitution creation; future monitoring required for spec conflicts or unworkable principles)
- Graders run and results (PASS/FAIL): Constitutional compliance grader not yet implemented; manual review confirms all mandatory sections present and complete
- Prompt variant (if applicable): N/A (baseline constitution creation)
- Next experiment (smallest change to try): Create spec for recurring tasks feature using constitution as authority; validate whether principles are sufficiently clear and enforceable during actual feature development
