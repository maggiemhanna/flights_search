# ✈️ Flights Search & Filtering Multi-Agent System

Welcome to the **Flights Search Multi-Agent System**! This project is a modular, event-driven travel platform built with **Google ADK (Agent Development Kit)**, **Google Gemini 2.5**, **FastAPI**, and **React**.

It enables users to search for simulated flights and interactively refine results through a conversational **ChatWidget**—supporting hard parameter filtering, deep semantic filtering with live web research, open-ended travel inspiration, and self-healing JSON correction.

---

## 🏗️ System Architecture

The application is architected as a set of autonomous microservices coordinated by a central gateway and connected to an interactive frontend.

![Architecture](architecture.png)

---

## 🌿 Branch Comparison & Execution Modes

This repository is organized into two primary branches tailored for different workflows:

| Feature / Mode | `local` Branch | `main` Branch |
| :--- | :--- | :--- |
| **Primary Purpose** | Local development, rapid iteration, and offline testing. | Production cloud deployment and microservice hosting. |
| **Backend Infrastructure** | Local **Uvicorn** ASGI servers running on separate `localhost` ports (`8001`–`8007`). | Containerized **Google Cloud Run** serverless services. |
| **Agent Inter-Communication** | Direct HTTP calls to local loopback (`http://127.0.0.1:<PORT>`). | HTTPS requests to Cloud Run service endpoints (`https://<service>-<id>.run.app`). |
| **Frontend Connection** | Connects to local Uvicorn servers (`:8005` for orchestrator, `:8006` for flight search). | Connects to deployed Cloud Run services. |
| **Integration Testing** | `test_microservice.py` targets local servers (`http://127.0.0.1:<PORT>`). | `test_microservice.py` targets deployed Cloud Run microservices. |
| **Execution Steps** | 1. Checkout `local`<br>2. Start 7 local Uvicorn servers<br>3. Run frontend (`npm run dev`) or test scripts. | 1. Checkout `main`<br>2. Build & deploy Cloud Run services (`./deploy_agents.sh`)<br>3. Deploy frontend container (`./deploy_frontend.sh`). |

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
│   ├── engage/              # Intent triage and routing microservice (:8001)
│   ├── filter/              # Deterministic parameter extraction microservice (:8002)
│   ├── filter_smart/        # Semantic filtering + live Google Search microservice (:8003)
│   ├── flights_search/      # Realistic flight search data simulation microservice (:8006)
│   ├── inspiration/         # Open-ended travel discovery microservice (:8007)
│   ├── json_parser/         # Self-healing JSON syntax & schema correction microservice (:8004)
│   └── orchestrator/        # Central FastAPI gateway coordinating the agents (:8005)
├── frontend/                # React + Vite frontend application & ChatWidget (:5173)
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
├── env.yaml                 # Root deployment config (PROJECT_ID and SERVICE_ACCOUNT)
└── requirements.txt         # Root Python dependencies
```

---

## 💻 Option A: Running Locally (`local` Branch)

In the `local` branch, all microservices and frontend communicate over `localhost` (`127.0.0.1`) on their designated ports.

### 1. Checkout the `local` Branch
```bash
git checkout local
```

### 2. Prerequisites & Environment Setup
- **Python >= 3.11**
- **Node.js >= 18**
- Authenticate with Google Cloud for Gemini / Vertex AI models:
```bash
gcloud auth application-default login
```

Create and activate a virtual environment, then install root dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Agent Environment Variables (`env.yaml`)
Ensure that all `env.yaml` files for the agents are updated with your own Google Cloud **Project ID** and **Location/Region**:
- `agents/engage/env.yaml`
- `agents/filter/env.yaml`
- `agents/filter_smart/env.yaml`
- `agents/flights_search/env.yaml`
- `agents/inspiration/env.yaml`
- `agents/json_parser/env.yaml`

Update the following keys in each file:
```yaml
GOOGLE_CLOUD_PROJECT: "<YOUR_GCP_PROJECT_ID>"
GOOGLE_CLOUD_LOCATION: "<YOUR_GCP_LOCATION>" # e.g., europe-west9, us-central1
```

*(Note: For `agents/filter_smart/env.yaml` and `agents/flights_search/env.yaml`, provide your `SERPAPI_KEY` if live search is used).*

### 4. Start Backend Microservices (Local Uvicorn Servers)
Run each agent in a separate terminal (or in background processes):

```bash
# Terminal 1: Engage Agent (Port 8001)
python -m agents.engage.main

# Terminal 2: Filter Agent (Port 8002)
python -m agents.filter.main

# Terminal 3: Smart Filter Agent (Port 8003)
python -m agents.filter_smart.main

# Terminal 4: JSON Parser Agent (Port 8004)
python -m agents.json_parser.main

# Terminal 5: Flights Search Simulator (Port 8006)
python -m agents.flights_search.main

# Terminal 6: Inspiration Agent (Port 8007)
python -m agents.inspiration.main

# Terminal 7: Central Orchestrator Gateway (Port 8005)
python -m agents.orchestrator.main
```

### 5. Start the Frontend
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser to interact with the flight search engine and conversational chat widget.

### 6. Running Tests Locally
In the `local` branch, tests can be run either in-memory or directly against the live local Uvicorn servers:

```bash
# 1. In-memory unit tests (FastAPI TestClient)
pytest

# Or run individual in-memory tests:
python -m tests.orchestrator.test
python -m tests.engage.test
python -m tests.filter.test
python -m tests.filter_smart.test
python -m tests.inspiration.test
python -m tests.json_parser.test
python -m tests.flights_search.test

# 2. Live HTTP Microservice tests (requires local Uvicorn servers to be running)
python -m tests.orchestrator.test_microservice
python -m tests.engage.test_microservice
python -m tests.filter.test_microservice
python -m tests.filter_smart.test_microservice
python -m tests.inspiration.test_microservice
python -m tests.json_parser.test_microservice
python -m tests.flights_search.test_microservice
```

---

## ☁️ Option B: Deploying to Google Cloud Run (`main` Branch)

In the `main` branch, each microservice is deployed as an independent container on Google Cloud Run. The services communicate with each other using their Cloud Run HTTPS URLs, and the frontend connects to those deployed endpoints.

### 1. Checkout the `main` Branch
```bash
git checkout main
```

### 2. Setup Google Cloud CLI & Deployment Environment
1. Ensure your `gcloud` CLI is logged in and configured with your target project:
   ```bash
   gcloud auth login
   gcloud config set project [$PROJECT_ID]
   ```

2. **Configure root `env.yaml`:**
   Before running any deployment scripts (`deploy_agent.sh`, `deploy_agents.sh`, `deploy_frontend.sh`), update the root `env.yaml` file with your Google Cloud **Project ID** and **Compute Service Account**:
   ```yaml
   PROJECT_ID: "<YOUR_GCP_PROJECT_ID>"
   SERVICE_ACCOUNT: "<YOUR_SERVICE_ACCOUNT_EMAIL>"
   ```
   *(e.g., `<PROJECT_NUMBER>-compute@developer.gserviceaccount.com`)*

3. **Configure Agent `env.yaml` Files:**
   Make sure all individual `agents/<agent>/env.yaml` files have your `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` set before deploying container images.

### 3. Deploy Backend Microservices to Cloud Run
You can deploy microservices individually or all together in parallel:

- **Deploy a Single Agent:**
  ```bash
  ./deploy_agent.sh <agent_name>

  # Examples:
  ./deploy_agent.sh orchestrator
  ./deploy_agent.sh filter_smart
  ./deploy_agent.sh engage
  ```

- **Deploy All Microservices Concurrently:**
  ```bash
  ./deploy_agents.sh
  ```

### 4. Deploy Frontend Container to Cloud Run
Build and deploy the React frontend container:
```bash
./deploy_frontend.sh
```

### 5. Running Tests Against Cloud Run Microservices
In the `main` branch, the `test_microservice.py` files are configured to test the live deployed Cloud Run endpoints:

```bash
python -m tests.orchestrator.test_microservice
python -m tests.engage.test_microservice
python -m tests.filter.test_microservice
python -m tests.filter_smart.test_microservice
python -m tests.inspiration.test_microservice
python -m tests.json_parser.test_microservice
python -m tests.flights_search.test_microservice
```

### Cloud Run Service Specifications
- **Region:** `europe-west9`
- **Platform:** Managed (`--allow-unauthenticated`)
- **Resources:** 2 CPU, 2Gi RAM
- **Scaling:** Minimum 1 instance (`--min-instances 1`, `--no-cpu-throttling`)
