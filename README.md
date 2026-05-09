# Regnology Vizor PS Chatbot

A Professional Services AI Chatbot built to assist users of **Regnology Vizor** — the leading regulatory reporting and data management platform.

## Overview

The Regnology Vizor PS Chatbot is an intelligent assistant designed to streamline professional services workflows, accelerate client onboarding, and provide contextual guidance within the Vizor ecosystem. It leverages AI/LLM capabilities to answer product questions, assist with configuration, and support regulatory compliance use cases.

## Features

- **Conversational AI Interface** — Natural language Q&A for Vizor product guidance
- **Regulatory Knowledge Base** — Pre-trained on Vizor documentation, regulatory frameworks (COREP, FINREP, AnaCredit, etc.)
- **Professional Services Support** — Assists PS consultants with implementation tasks
- **Contextual Recommendations** — Suggests relevant Vizor modules and configurations
- **Multi-turn Dialogue** — Maintains conversation context for complex queries
- **Audit Logging** — Tracks interactions for compliance and review

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React / TypeScript |
| Backend | Python (FastAPI) |
| LLM | OpenAI GPT-4 / Azure OpenAI |
| Vector Store | Pinecone / ChromaDB |
| Auth | Azure AD / OAuth 2.0 |
| Deployment | Docker / Kubernetes |

## Project Structure

```
Regnology-Vizor-PS-Chatbot/
├── frontend/           # React UI
├── backend/            # FastAPI service
│   ├── api/            # REST endpoints
│   ├── chains/         # LangChain pipelines
│   ├── embeddings/     # Document embedding logic
│   └── models/         # Data models
├── data/               # Knowledge base / training docs
├── infra/              # Infrastructure as code
├── docs/               # Additional documentation
│   └── design.md       # Architecture & design decisions
└── tests/              # Unit and integration tests
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker Desktop
- Azure OpenAI or OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yuanfengli168/Regnology-Vizor-PS-Chatbot.git
cd Regnology-Vizor-PS-Chatbot

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
npm run dev
```

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
OPENAI_API_KEY=your_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
VECTOR_STORE_API_KEY=your_vector_store_key
DATABASE_URL=your_database_connection_string
```

## Documentation

- [Design Document](design.md) — Architecture decisions and system design
- [API Reference](docs/api.md) — REST API documentation
- [Deployment Guide](docs/deployment.md) — Kubernetes / Docker deployment

## Contributing

This is an internal Regnology Professional Services project. Please follow the internal contribution guidelines and code review process before submitting changes.

## License

Proprietary — Regnology GmbH. All rights reserved.
