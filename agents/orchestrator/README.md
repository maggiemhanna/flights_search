# 🎛️ Orchestrator Service

The **Orchestrator Service** is the central coordination engine of the multi-agent system, built with **FastAPI** and pure Python. Rather than being an LLM agent itself, it acts as a deterministic **Rule-Based Routing & Aggregation Gateway** that connects the frontend interface (ChatWidget) with all specialized backend agent microservices (`engage`, `filter`, `filter_smart`, and `inspiration`).

---

## 🌟 How the Orchestrator Works

### 1. Architectural Role & Flow
- **Gateway & Coordinator:** Sits directly behind the React frontend, processing conversational turns alongside the current search context and flight listings.
- **Microservice Orchestration:**
  ```mermaid
  graph TD
      Client([Frontend / ChatWidget]) -->|POST /run-orchestrator| Orch[Orchestrator Service :8005]
      
      Orch -->|1. Triage Intent| Engage[Engage Service :8001]
      Engage -->|agent_decision, agent_response| Orch
      
      Orch -->|decision: continue| ReturnClient[Unified Response `agent_response` to Frontend]
      Orch -->|decision: filter| Filter[Filter Service :8002]
      Orch -->|decision: smart_filter| SmartFilter[Smart Filter Service :8003]
      Orch -->|decision: inspiration_agent| Inspiration[Inspiration Service :8007]
      
      Filter -->|filter_type, filter_value, filter_response| Orch
      SmartFilter -->|flights_output, filter_response| Orch
      Inspiration -->|flights_search_output, inspiration_response| Orch
      
      Orch --> ReturnClient
  ```

### 2. Execution Pipeline
1. **Engage Triage (`call_engage_api`):**
   - Sends `user_message` and `conversational_history` to the `engage` microservice.
   - Receives `agent_decision` (`continue`, `filter`, `smart_filter`, `inspiration_agent`) and `agent_response`.
2. **Dynamic Sub-Agent Routing:**
   - **`continue`**: Returns immediately with the conversational guidance message.
   - **`filter`**: Calls the `filter` microservice to extract deterministic parameters (`direct`, `max_price`, `max_stops`). The frontend or backend can apply these with 100% precision.
   - **`smart_filter`**: Dispatches the raw flight listings (`flights_input`) and user preferences to the `filter_smart` microservice for semantic evaluation and live web research, returning filtered `flights_output`.
   - **`inspiration_agent`**: Sends current search context to the `inspiration` microservice to discover new destinations or date ranges (`flights_search_output`) and travel suggestions (`inspiration_response`).
3. **Envelope Packaging:**
   - Aggregates and merges responses into a single structured `OrchestratorOutput` payload for immediate UI state updates.

---

## 📁 File Structure & Breakdown

| File | Purpose |
| :--- | :--- |
| **[`main.py`](main.py)** | The core FastAPI application. Implements CORS middleware, microservice HTTP clients (`call_engage_api`, `call_filter_api`, `call_smart_filter_api`, `call_inspiration_agent_api`), routing logic, and exposes REST endpoints (`/` and `/run-orchestrator`). Runs Uvicorn on port `8005` when executed directly. |
| **[`schema.py`](schema.py)** | Defines Pydantic models for data contracts: `Flight`, `FlightParams`, `OrchestratorInput`, and `OrchestratorOutput`. |
| **[`requirements.txt`](requirements.txt)** | Python dependencies required by the orchestrator service (e.g., `fastapi`, `uvicorn`, `pydantic`, `requests`, `PyYAML`, `coloredlogs`). |

---

## 📊 Data Schemas

### Request Model: `OrchestratorInput`
```json
{
  "user_message": "Show me flights with good WiFi departing in the morning",
  "conversational_history": [
    "user: Search flights from Paris to New York on 2026-05-10",
    "bot: Found 15 flights matching your search."
  ],
  "flights_search_input": {
    "origin": "Paris",
    "destination": "New York",
    "departure_date": "2026-05-10",
    "return_date": "2026-05-20",
    "passengers": 1
  },
  "flights_input": [
    {
      "origin": "Paris (CDG)",
      "destination": "New York (JFK)",
      "departure_date": "2026-05-10",
      "return_date": "2026-05-20",
      "departure_time": "10:30",
      "arrival_time": "13:00",
      "return_time": "17:30",
      "return_arrival_time": "06:45 +1",
      "price": "520 EUR",
      "airline": "Air France",
      "flight_number": "AF006",
      "stops": 0,
      "stopover_cities": []
    }
  ]
}
```

### Response Model: `OrchestratorOutput` (Envelope)
```json
{
  "status": "success",
  "results": {
    "agent_response": "I'm filtering the flights to find morning options with high-speed WiFi.",
    "agent_decision": "smart_filter",
    "filter_response": "Filtered out afternoon flights. Verified that Air France AF006 offers satellite WiFi.",
    "flights_output": [
      {
        "origin": "Paris (CDG)",
        "destination": "New York (JFK)",
        "departure_date": "2026-05-10",
        "return_date": "2026-05-20",
        "departure_time": "10:30",
        "arrival_time": "13:00",
        "return_time": "17:30",
        "return_arrival_time": "06:45 +1",
        "price": "520 EUR",
        "airline": "Air France",
        "flight_number": "AF006",
        "stops": 0,
        "stopover_cities": []
      }
    ]
  }
}
```

---

## 🔌 API Endpoints

### 1. Health Check
- **Method:** `GET`
- **Path:** `/`
- **Response:**
  ```json
  {
    "message": "Orchestrator Agent Service is running. Use the /run-orchestrator endpoint via POST."
  }
  ```

### 2. Run Orchestrator
- **Method:** `POST`
- **Path:** `/run-orchestrator`
- **Headers:** `Content-Type: application/json`
- **Body:** `OrchestratorInput`
- **Example cURL:**
  ```bash
  curl -X POST "http://localhost:8005/run-orchestrator" \
    -H "Content-Type: application/json" \
    -d '{
      "user_message": "Show only direct flights under 600 euros",
      "conversational_history": [],
      "flights_search_input": {
        "origin": "London",
        "destination": "Rome",
        "departure_date": "2026-06-01",
        "return_date": "2026-06-10",
        "passengers": 1
      },
      "flights_input": []
    }'
  ```

---

## 🚀 Running Locally

### 1. Prerequisites
- Python >= 3.11
- Running downstream microservices or accessible deployed endpoints (`engage`, `filter`, `filter_smart`, `inspiration`).

### 2. Installation
From the repository root (`flights_search/`):
```bash
pip install -r agents/orchestrator/requirements.txt
```

### 3. Start the Service
You can start the service directly using Python:
```bash
python -m agents.orchestrator.main
```
Or via Uvicorn:
```bash
uvicorn agents.orchestrator.main:api --host 127.0.0.1 --port 8005 --reload
```

---

## 🧪 Testing

Run the automated test suite using `pytest` or directly with Python from the root directory:

```bash
# Using pytest
pytest tests/orchestrator/test.py

# Or running the test script directly
python -m tests.orchestrator.test
```
