# Regnology Vizor PS Chatbot — Design Document

## 1. Overview

This document describes the architecture, design decisions, and technical approach for the **Regnology Vizor PS Chatbot** — an AI-powered assistant for Professional Services teams and clients working with the Vizor regulatory reporting platform.

---

## 2. Goals & Non-Goals

### Goals
- Provide accurate, context-aware answers to Vizor product and regulatory questions
- Accelerate PS consultant workflows (implementation, configuration, troubleshooting)
- Reduce time-to-value for new Vizor clients through guided onboarding
- Support multi-turn, stateful conversations with memory

### Non-Goals
- Replace human PS consultants for complex bespoke engagements
- Process live production regulatory data
- Provide legally binding regulatory advice

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Client Layer                           │
│           Web UI (React)  │  Vizor Portal Embed (iFrame)        │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS / WebSocket
┌───────────────────────────▼─────────────────────────────────────┐
│                       API Gateway / BFF                         │
│                  FastAPI  |  Auth (Azure AD)                     │
└────────────┬──────────────────────────────┬────────────────────┘
             │                              │
┌────────────▼────────────┐   ┌─────────────▼──────────────────┐
│   Conversation Service   │   │      RAG Pipeline              │
│  - Session management    │   │  - Query embedding             │
│  - History storage       │   │  - Vector similarity search    │
│  - Context window mgmt   │   │  - Document retrieval          │
└────────────┬────────────┘   └─────────────┬──────────────────┘
             │                              │
┌────────────▼──────────────────────────────▼──────────────────┐
│                     LLM Orchestration Layer                    │
│              LangChain / LlamaIndex  |  Prompt Templates       │
└────────────────────────────┬─────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
┌────────▼────────┐ ┌────────▼────────┐ ┌───────▼────────┐
│  Azure OpenAI   │ │  Vector Store   │ │  Knowledge DB  │
│  GPT-4 / GPT-4o │ │  (Pinecone /    │ │  (PostgreSQL)  │
│                 │ │   ChromaDB)     │ │                │
└─────────────────┘ └─────────────────┘ └────────────────┘
```

---

## 4. Key Components

### 4.1 Frontend (React / TypeScript)

- **Chat interface** with streaming token output
- Markdown rendering for structured responses (tables, code blocks)
- Session persistence via browser localStorage
- Theme-aligned with Regnology / Vizor brand guidelines

### 4.2 Backend API (FastAPI)

- RESTful + WebSocket endpoints for chat sessions
- JWT-based auth via Azure AD
- Rate limiting and request validation
- Async I/O for high-concurrency support

### 4.3 RAG (Retrieval-Augmented Generation) Pipeline

1. **Document Ingestion** — Vizor product docs, release notes, regulatory frameworks (COREP, FINREP, AnaCredit, DORA) are parsed and chunked
2. **Embedding** — Chunks embedded via `text-embedding-3-large`
3. **Vector Store** — Embeddings stored in Pinecone (production) / ChromaDB (local dev)
4. **Query Flow** — User query → embed → top-k similarity search → inject into LLM context window

### 4.4 Conversation Memory

- **Short-term**: Last N messages passed in LLM context
- **Long-term**: Summarized session history stored in PostgreSQL
- **Namespace isolation**: Per-user, per-session memory partitioning

### 4.5 Prompt Engineering

- System prompt defines assistant persona, scope, and tone
- Few-shot examples cover common Vizor PS scenarios
- Guardrails prevent hallucination of regulatory specifics
- Fallback responses route complex queries to human PS team

---

## 5. Data Flow

```
User Message
     │
     ▼
[Input Validation & Sanitization]
     │
     ▼
[Auth Check + Rate Limiter]
     │
     ▼
[Load Conversation History]
     │
     ├──► [Embed User Query]
     │         │
     │         ▼
     │    [Vector Search → Retrieve Top-K Docs]
     │         │
     ▼         ▼
[Build Prompt: System + History + Retrieved Docs + User Query]
     │
     ▼
[LLM API Call (streaming)]
     │
     ▼
[Stream tokens to client]
     │
     ▼
[Persist message to conversation history]
     │
     ▼
[Audit Log]
```

---

## 6. Security Design

| Concern | Approach |
|---------|----------|
| Authentication | Azure AD OAuth 2.0 / OIDC |
| Authorization | Role-based (PS Consultant, Client User, Admin) |
| Data in Transit | TLS 1.3 everywhere |
| Data at Rest | AES-256 encryption for stored conversations |
| PII Handling | PII detection + redaction before LLM submission |
| Prompt Injection | Input sanitization, output filtering, system prompt hardening |
| API Keys | Azure Key Vault — never stored in code or env files in prod |
| Audit Trail | All interactions logged with user ID, timestamp, session ID |

---

## 7. Regulatory Knowledge Base

### Document Sources
- Vizor product documentation (all modules)
- EBA / ECB reporting frameworks: COREP, FINREP, AnaCredit, IREF, DORA
- Internal Regnology PS runbooks and implementation guides
- Release notes and changelogs

### Ingestion Pipeline
- Scheduled nightly refresh for updated docs
- Version-tagged embeddings to support rollback
- Human review queue for flagged low-confidence responses

---

## 8. Scalability & Deployment

- **Containerized** via Docker; orchestrated with Kubernetes (AKS)
- **Horizontal scaling** for API and conversation services
- **Caching layer** (Redis) for frequently asked questions
- **Blue/green deployment** for zero-downtime releases
- **Monitoring**: Azure Monitor + Application Insights + Grafana dashboards

---

## 9. Open Questions / Future Considerations

- [ ] Fine-tuning a domain-specific model on Vizor PS data
- [ ] Integration with Vizor ticketing / case management system
- [ ] Voice interface for hands-free PS consultant support
- [ ] Multilingual support (DE, FR, IT, ES) for EU regulatory reporting clients
- [ ] Feedback loop: thumbs up/down training signal for RLHF

---

## 10. Revision History

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| 0.1 | 2026-05-09 | Jacky Li | Initial draft |
