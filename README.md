# ✈️ Flights Search & Filtering Multi-Agent System

Welcome to the **Flights Search Multi-Agent System**! This repository contains a cutting-edge, modular architecture for simulating flight searches and applying complex filters using **Natural Language Queries**. 

Leveraging the **Google ADK (Agent Development Kit)** and **FastAPI**, this project demonstrates how to orchestrate multiple specialized LLM agents alongside deterministic Python logic to create a robust, reliable, and user-friendly experience.

---

## 🏗️ Architectural Overview

The system is split into two main domains:
1.  **Simulated Search & Data Generation:** An independent agent that acts as a mock flight search engine.
2.  **Conversational Flow & Filtering Pipeline:** A set of agents coordinated by a rule-based engine (FastAPI) to parse intent and apply both hard (deterministic) and soft (semantic) filters.

### 🧩 System Flow Diagram

```mermaid
graph TD
    User([User Query]) --> Orchestrator{Orchestrator Service <br/><i>(Pure Python FastAPI)</i>}
    
    %% Intent Detection
    Orchestrator --> Engage[Engage Agent <br/><i>(Intent Classifier)</i>]
    Engage -->|agent_decision| Orchestrator
    
    %% Routing
    Orchestrator -->|Decision: filter| FilterAgent[Filter Agent <br/><i>(NL to Parameters)</i>]
    Orchestrator -->|Decision: smart_filter| SmartFilter[Smart Filter Agent <br/><i>(Semantic Filtering + Research)</i>]
    
    %% Output
    FilterAgent -->|Structured Params| DeterministicOutput[Reliable Backend Update]
    SmartFilter -->|Pruned List| StructuredOutput[Filtered JSON Results]
    
    %% Flights Search (Independent)
    FlightsSim[Flights Search Agent <br/><i>(Simulator)</i>] -.->|Generates Data| SmartFilter
```

---

## 🤖 Meet the Agents

### 1. 🔍 Flights Search Agent (`flights_search`)
The **Flights Search Agent** is the foundation of data simulation in this project. It acts as an independent, expert flight search simulator.

-   **Role:** Generates a realistic and diverse list of flights based on primary search criteria.
-   **Model:** `gemini-2.5-flash`
-   **Capabilities:**
    -   Takes input like `origin`, `destination`, `dates`, and `passengers`.
    -   Synthesizes simulated flight numbers, airlines, departure/arrival times, stops, and prices.
    -   Guarantees a rich dataset of **15 flights** per request to ensure downstream filtering has enough variance.

---

### 2. 🤝 Engage Agent (`engage`)
The **Engage Agent** acts as the primary triage or receptionist for user requests. 

-   **Role:** Analyzes user messages alongside conversational history to classify intent.
-   **Decisions:**
    -   `continue`: Solicits more information from the user.
    -   `filter`: Directs the flow to standard, hard-constraint filtering.
    -   `smart_filter`: Directs the flow to semantic, soft-constraint filtering.
    -   `inspiration_agent`: (Roadmap) Handles open-ended vacation planning.
-   **Importance:** By offloading routing to an LLM, the system can understand messy natural language without complex regex or keyword matching.

---

### 3. 🔢 Filter Agent (`filter`) — *Translating NL to Deterministic Parameters*
The **Filter Agent** is a specialized LLM that bridges the gap between natural language and traditional, programmatic databases.

-   **Role:** Extracts standard parameters for reliable filtering.
-   **Supported Scopes:** `direct` (direct flights), `max_price`, `max_stops`.
-   **Mechanical Flow:** Instead of filtering data itself (which can risk hallucination), the agent outputs pure JSON parameters (e.g., `filter_type="max_price"`, `filter_value=500`).
-   **Why it's essential:** This allows standard, rule-based database queries to execute the filter *without* relying on LLM vibes, ensuring 100% accurate results.

---

### 4. 🧠 Smart Filter Agent (`filter_smart`) — *Semantic & Research-Enabled*
The **Smart Filter Agent** handles queries that rigid databases cannot solve (e.g., "I want flights with good WiFi" or "Show me airlines with modern fleets").

-   **Role:** Evaluates "Soft Constraints" using contextual reasoning and external research.
-   **Capabilities:**
    -   Parses lists of flights and prunes out candidates that fail semantic tests.
    -   Triggers parallel **Google Search API** queries to research things like WiFi availability or legroom for specific flight numbers/airlines.
-   **Output:** Prunes the `flights_input` and returns a curated JSON array alongside a human explanation of the deductions.

---

### 🔢 The Orchestrator Logic: Bridging Natural Language to Deterministic Actions

The `orchestrator` is not an LLM agent itself; it is a **pure Python/FastAPI service** that implements rule-based orchestration. It manages the pipeline of passing data between agents to achieve reliable results based on user queries and history.

#### How it works:
1.  **Understand Intent:** The Orchestrator receives a user query and passes it to the `engage` agent.
2.  **Evaluate Decision:**
    -   **Standard Filtering (Deterministic Extraction):** If `engage` decides the query is a standard filter (e.g., "Under $500"), the Orchestrator routes it to the **`filter` agent**.
        -   The `filter` agent translates this into a **deterministic parameter** (e.g., `filter_type='max_price'`, `filter_value=500`).
        -   The orchestrator returns these parameters to the system, enabling a traditional database/backend to execute the filter *without* risk of LLM hallucinations.
    -   **Semantic Filtering (Smart Pruning):** If `engage` decides it's a soft constraint (e.g., "Show me flights with good WiFi"), it routes to **`filter_smart`**.
        -   The `filter_smart` agent reads the actual flight list, research topics, and prunes the flights directly, returning a filtered subset of flights (`flights_output`).

By combining the **`engage`** agent for intent parsing and the **`filter`** agent for parameter extraction, the `orchestrator` enables users to interact with complex, deterministic systems using natural language, ensuring accuracy and reliability.


---

## 🚀 Getting Started

### Prerequisites
- Python >= 3.11
- GEMINI_API_KEY environment variable set.

### Installation
```bash
# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Services
Each agent runs as a separate micro-service on a dedicated port. Start them in separate terminals or as background processes:

| Service | Port | Command |
| :--- | :--- | :--- |
| **Flights Search Simulator** | `8000` | `python -m agents.flights_search.main` |
| **Engage Agent** | `8001` | `python -m agents.engage.main` |
| **Filter Agent** | `8002` | `python -m agents.filter.main` |
| **Smart Filter Agent** | `8003` | `python -m agents.filter_smart.main` |
| **Orchestrator Core** | `8004` | `python -m agents.orchestrator.main` |

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
