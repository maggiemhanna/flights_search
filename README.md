# ✈️ Flights Search & Filtering Multi-Agent System

Welcome to the **Flights Search Multi-Agent System**! This project is a modular, event-driven travel platform built with **Google ADK (Agent Development Kit)**, **Google Gemini 2.5**, **FastAPI**, and **React**.

It enables users to search for simulated flights and interactively refine results through a conversational **ChatWidget**—supporting hard parameter filtering, deep semantic filtering with live web research, open-ended travel inspiration, and self-healing JSON correction.

---

## 🏗️ System Architecture

The application is architected as a set of autonomous microservices coordinated by a central gateway and connected to an interactive frontend.

![Architecture](architecture.png)

---

## 🤖 Microservices & Agents Overview

Each agent runs as an independent FastAPI microservice with its own dedicated documentation:

| Service | Port | Model / Tech | Role & Description | Documentation |
| :--- | :---: | :--- | :--- | :---: |
| **Orchestrator** | `8005` | FastAPI / Python | **Central Coordinator**: Triages user requests via `engage` and delegates to appropriate expert agents. | [README](agents/orchestrator/README.md) |
| **Engage Agent** | `8001` | Gemini 2.5 Pro | **Triage Specialist**: Analyzes user intent to route to `continue`, `filter`, `smart_filter`, or `inspiration_agent`. | [README](agents/engage/README.md) |
| **Filter Agent** | `8002` | Gemini 2.5 Pro | **Filter Extraction**: Translates natural language into deterministic database parameters (`direct`, `max_price`, `max_stops`). | [README](agents/filter/README.md) |
| **Smart Filter Agent** | `8003` | Gemini 2.5 Pro + Search | **Semantic Filter**: Evaluates qualitative amenities (WiFi, legroom, aircraft) via contextual reasoning and live Google Search. | [README](agents/filter_smart/README.md) |
| **Inspiration Agent** | `8007` | Gemini 2.5 Pro | **Discovery Architect**: Suggests destinations and date ranges for open-ended travel requests (*"somewhere sunny in December"*). | [README](agents/inspiration/README.md) |
| **Flights Search Agent** | `8006` | Gemini 2.5 Flash Lite | **Flight Simulator**: Generates 15 realistic, route-appropriate flight options obeying temporal and timezone logic. | [README](agents/flights_search/README.md) |
| **JSON Parser Agent** | `8004` | Gemini 2.5 Pro | **Structure Corrector**: Repairs malformed JSON outputs and guarantees strict schema compliance. | [README](agents/json_parser/README.md) |
| **Frontend** | `5173` | React / Vite | **User Interface**: Flight search exploration view with conversational ChatWidget. | [frontend/](frontend/) |

---

## 📁 Repository Structure

```text
flights_search/
├── agents/
│   ├── engage/              # Intent triage and routing microservice
│   ├── filter/              # Deterministic parameter extraction microservice
│   ├── filter_smart/        # Semantic filtering + live Google Search microservice
│   ├── flights_search/      # Realistic flight search data simulation microservice
│   ├── inspiration/         # Open-ended travel discovery microservice
│   ├── json_parser/         # Self-healing JSON syntax & schema correction microservice
│   └── orchestrator/        # Central FastAPI gateway coordinating the agents
├── frontend/                # React + Vite frontend application & ChatWidget
├── tests/                   # Microservice integration and unit tests
│   ├── engage/
│   ├── filter/
│   ├── filter_smart/
│   ├── flights_search/
│   ├── inspiration/
│   ├── json_parser/
│   └── orchestrator/
├── utils/                   # Shared logging and formatting utilities
├── deploy_agent.sh          # Helper script to deploy a single agent to Cloud Run
├── deploy_agents.sh         # Helper script to deploy all microservices to Cloud Run
├── deploy_frontend.sh       # Helper script to deploy the React frontend to Cloud Run
└── requirements.txt         # Root Python dependencies
```

---

## 🚀 Running Locally

### 1. Prerequisites
- **Python >= 3.11**
- **Node.js >= 18** (for frontend)
- Google Cloud / Vertex AI credentials configured (or `gcloud auth application-default login`).

### 2. Backend Setup
Create and activate a virtual environment, then install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Start Backend Microservices
Run the microservices in separate terminals (or in the background):

```bash
# Terminal 1: Engage Agent
python -m agents.engage.main

# Terminal 2: Filter Agent
python -m agents.filter.main

# Terminal 3: Smart Filter Agent
python -m agents.filter_smart.main

# Terminal 4: JSON Parser Agent
python -m agents.json_parser.main

# Terminal 5: Flights Search Simulator
python -m agents.flights_search.main

# Terminal 6: Inspiration Agent
python -m agents.inspiration.main

# Terminal 7: Central Orchestrator
python -m agents.orchestrator.main
```

### 4. Start the Frontend
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser to interact with the flight search engine and chat widget.

---

## 🧪 Testing

You can run automated tests for any microservice using `pytest` or Python:

```bash
# Run all tests via pytest
pytest

# Test a specific agent (e.g. Orchestrator or Engage)
python -m tests.orchestrator.test
python -m tests.engage.test
python -m tests.filter.test
python -m tests.filter_smart.test
python -m tests.inspiration.test
python -m tests.json_parser.test
python -m tests.flights_search.test
```

---

## ☁️ Deploying to Google Cloud Run

The repository includes preconfigured `cloudbuild.yaml` files and deployment bash scripts to deploy each microservice as a containerized Google Cloud Run service.

### 1. Setup Google Cloud CLI
Ensure your `gcloud` CLI is logged in and configured with your project:
```bash
gcloud auth login
gcloud config set project [$PROJECT_ID]
```

### 2. Deploy a Single Microservice
To deploy or update a specific agent (e.g. `orchestrator` or `filter_smart`):
```bash
./deploy_agent.sh <agent_name>

# Examples:
./deploy_agent.sh orchestrator
./deploy_agent.sh filter_smart
./deploy_agent.sh engage
```

### 3. Deploy All Microservices (Parallel)
To build and deploy all backend microservices concurrently using Cloud Build:
```bash
./deploy_agents.sh
```

### 4. Deploy Frontend
To build and deploy the React frontend container to Cloud Run:
```bash
./deploy_frontend.sh
```

### Cloud Run Service Specifications
- **Region:** `europe-west9`
- **Platform:** Managed (`--allow-unauthenticated`)
- **Resources:** 2 CPU, 2Gi RAM
- **Scaling:** Minimum 1 instance (`--min-instances 1`, `--no-cpu-throttling`)
