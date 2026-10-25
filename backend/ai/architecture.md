# Campus AI Assistant — System Architecture & Security Boundaries

## 1. Executive Overview
The Campus AI Assistant is a secure, role-aware agentic copilot built into the Smart Campus Management System. It operates strictly through controlled Django services, model forms, and verified tool registries without direct database access.

## 2. Layered Architecture

```
User (Voice / Text UI)
        │
        ▼
POST /ai/chat/ (Authentication & CSRF Check)
        │
        ▼
CampusAIService (Intent Detection & Session Context)
        │
        ▼
Role & Object Authorization Layer
        │
        ▼
Existing Django Service / Form / Model Logic
        │
        ▼
Post-Write DB Verification & Action Preview
        │
        ▼
Structured Response / UI Navigation Action
```

## 3. Security Boundaries
- **No Direct SQL Execution**: AI never generates or executes raw SQL queries.
- **No Arbitrary Code Execution**: Zero `eval()`, `exec()`, or dynamic script generation.
- **Secret Protection**: Passwords, OTPs, API keys, and session secrets are strictly shielded from response payloads.
- **Confirmation Preview**: High-risk write actions (updates, leave approvals, announcements) generate server-side session-verified confirmation cards.
