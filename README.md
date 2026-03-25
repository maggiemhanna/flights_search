# ✈️ Flights Search & Filtering Multi-Agent System

Welcome to the **Flights Search Multi-Agent System**! This repository contains a cutting-edge, modular architecture for simulating flight searches and applying complex filters using **Natural Language Queries**.

Leveraging the **Google ADK (Agent Development Kit)** and **FastAPI**, this project demonstrates how to orchestrate multiple specialized LLM agents alongside deterministic Python logic to create a robust, reliable, and user-friendly experience.

It now also includes a beautifully crafted React frontend with an interactive conversational ChatWidget that talks directly to the backend Orchestrator!

---

## 🏗️ Architectural Overview

The system is split into multiple main domains:
1.  **Frontend Interface:** A beautiful React application to explore flights and engage in conversational search via the ChatWidget.
2.  **Simulated Search & Data Generation:** An independent agent that acts as a mock flight search engine.
3.  **Conversational Flow & Filtering Pipeline:** A set of agents coordinated by a rule-based engine (`Orchestrator` in FastAPI) to parse intent, process conversational history, and apply both hard (deterministic) and soft (semantic) filters, or even inspire a whole new journey.
4.  **Formatting & Parsing Helpers:** Agents operating in the background to ensure structured JSON output.

### 🧩 System Flow Diagram

```mermaid
graph TD
    User([User + ChatWidget]) --> Orchestrator{Orchestrator Service <br/><i>(Pure Python FastAPI)</i>}
    
    %% Intent Detection
    Orchestrator <--> Engage[Engage Agent <br/><i>(Intent Classifier)</i>]
    
    %% Routing Decisions
    Orchestrator -->|Decision: filter| FilterAgent[Filter Agent <br/><i>(NL to Parameters)</i>]
    Orchestrator -->|Decision: smart_filter| SmartFilter[Smart Filter Agent <br/><i>(Semantic Filtering + Research)</i>]
    Orchestrator -->|Decision: inspiration_agent| InspirationAgent[Inspiration Agent <br/><i>(Destination/Date Inspiration)</i>]
    
    %% Output Handling
    FilterAgent --> DeterministicOutput[Reliable Backend Update]
    SmartFilter --> StructuredOutput[Filtered JSON Results]
    InspirationAgent --> NewParamsOutput[Dynamic Parameter Updates]
    
    %% Helper
    Orchestrator <--> JsonParser[JSON Parser Agent <br/><i>(Structured Output Corrector)</i>]
    
    %% Flights Search (Independent)
    FlightsSim[Flights Search Agent <br/><i>(Simulator)</i>] -.->|Generates Data| SmartFilter
```

---

## 🤖 Meet the Agents

### 1. 🔍 Flights Search Agent (`flights_search`)
The foundation of data simulation in this project.
-   **Role:** Generates a realistic and diverse list of flights based on primary search criteria.

### 2. 🤝 Engage Agent (`engage`)
The primary triage or receptionist for user requests.
-   **Role:** Analyzes user messages alongside conversational history to classify intent.
-   **Decisions:**
    -   `continue`: Solicits more information.
    -   `filter`: Standard, hard-constraint filtering.
    -   `smart_filter`: Semantic, soft-constraint filtering.
    -   `inspiration_agent`: Hand-off to the Inspiration agent for open-ended destination or date discovery.

### 3. 🔢 Filter Agent (`filter`) — *Translating NL to Deterministic Parameters*
The **Filter Agent** is a specialized LLM that bridges the gap between natural language and traditional, programmatic databases.

-   **Role:** Extracts standard parameters for reliable filtering.
-   **Supported Scopes:** `direct` (direct flights), `max_price`, `max_stops`.
-   **Mechanical Flow:** Instead of filtering data itself (which can risk hallucination), the agent outputs pure JSON parameters (e.g., `filter_type="max_price"`, `filter_value=500`).
-   **Why it's essential:** This allows standard, rule-based database queries to execute the filter *without* relying on LLM vibes, ensuring 100% accurate results.

---

### 4. 🧠 Smart Filter Agent (`filter_smart`)
Handles queries that rigid databases cannot solve (e.g., "I want flights with good WiFi").
-   **Role:** Evaluates "Soft Constraints" using contextual reasoning over the actual flight payload.

### 5. 💡 Inspiration Agent (`inspiration`)
A creative companion for the indecisive traveler.
-   **Role:** Analyzes requests like "I want to travel somewhere sunny" or "I want to fly in June" and intelligently suggests new destinations and automatically updates the travel parameters context.

### 6. 🛠️ JSON Parser Agent (`json_parser`)
A specialized structural assistant.
-   **Role:** Validates, structures, and occasionally corrects text chunks out of LLM responses to enforce perfectly-formatted JSON schemas for reliable cross-agent communication.

---

## 🔢 The Orchestrator Logic

The `orchestrator` is not an LLM agent; it is a **pure Python/FastAPI service**. It sits directly behind the ChatWidget, sending the user's history and queries to the `engage` agent, and delegating the follow-up logic to the respective expert agents (`filter`, `filter_smart`, or `inspiration`). It returns a structured JSON payload that the frontend can read easily, immediately updating the search inputs on the screen and repopulating new flight listings if instructed.

---

## 🚀 Getting Started

### Prerequisites
- Python >= 3.11
- Node.js (for frontend)
- `GEMINI_API_KEY` environment variable set.

### Installation
**Backend:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### Running the Services
Start the backend services as background processes or in separate terminals:

| Service | Port | Command |
| :--- | :--- | :--- |
| **Engage Agent** | `8001` | `python -m agents.engage.main` |
| **Filter Agent** | `8002` | `python -m agents.filter.main` |
| **Smart Filter Agent** | `8003` | `python -m agents.filter_smart.main` |
| **JSON Parser Agent** | `8004` | `python -m agents.json_parser.main` |
| **Orchestrator Core** | `8005` | `python -m agents.orchestrator.main` |
| **Flights Search Simulator** | `8006` | `python -m agents.flights_search.main` |
| **Inspiration Agent** | `8007` | `python -m agents.inspiration.main` |

Start the frontend application:
```bash
cd frontend
npm run dev
```

### Testing
You can run tests for each agent or run all integrations via standard `pytest`:
```bash
# Run all tests
pytest tests/
```
You can also run the orchestrator tests manually via:
```bash
python tests/orchestrator/test.py
```


---
*Developed with ❤️ using Google ADK.*
