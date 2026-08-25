# ✈️ Flights Search Agent Service

The **Flights Search Agent** is a dedicated microservice built with **Google ADK (Agent Development Kit)** and **FastAPI**. It acts as a realistic **Global Flight Data Simulator**, generating high-fidelity flight search results based on user-provided travel criteria (origin, destination, dates, passengers, and budget/stop filters).

---

## 🌟 How the Agent & Backend Work

### 1. The Agent Architecture (`Google ADK` + `Gemini 2.5 Flash Lite`)
- **Role:** Acts as a mock flight search engine / simulator producing realistic airline itineraries across budget, standard, and premium carriers.
- **Model:** Powered by Google's `gemini-2.5-flash-lite` through `google-adk`.
- **Planner & Performance:** Configured with `BuiltInPlanner` with thinking disabled (`thinking_budget=0`) for maximum speed, minimal latency, and consistent structured output.
- **Simulation Rules & Temporal Logic:**
  - Generates exactly 15 diverse flight options per query.
  - Accounts for flight duration, time zones, and overnight flights (marking next-day arrivals with `+1` or `+2`).
  - Uses realistic IATA flight numbers, route-appropriate airlines, and multiple city airport codes (e.g., LHR, LGW, STN for London; CDG, ORY for Paris).
  - Strictly adheres to filter criteria such as `max_price`, `max_stops`, or `direct` only.
- **Data Contracts:** Input and output data formats are enforced using **Pydantic** models (`FlightsSearchInput` and `FlightsSearchOutput`).

### 2. The FastAPI Backend Architecture
- **Framework:** FastAPI with Uvicorn ASGI server.
- **Environment Setup:** Loads environment settings (such as Vertex AI project and region) from `env.yaml` on startup.
- **CORS:** Configured to allow cross-origin requests from frontends and orchestrator microservices.
- **Per-Request Session Isolation:**
  - For each incoming request, a unique `session_id` and `user_id` are generated using `uuid4()`.
  - An `InMemorySessionService` is instantiated with the initial state containing the user's search parameters.
  - An ADK `Runner` executes the agent with the prompt `"Follow the system instructions."` in debug mode.
  - The model's response parts are extracted and parsed into JSON.

---

## 📁 File Structure & Breakdown

| File | Purpose |
| :--- | :--- |
| **[`agent.py`](agent.py)** | Instantiates the Google ADK `Agent` (`flights_search`) using `Gemini(model="gemini-2.5-flash-lite")`, attaches system instructions, schemas, planner configuration, and wraps the root agent into an ADK `App`. |
| **[`main.py`](main.py)** | The core FastAPI backend application. Manages environment variables, CORS middleware, session and runner execution lifecycle, and exposes REST endpoints (`/` and `/run-flights-search`). Runs Uvicorn on port `8006` when executed directly. |
| **[`prompt.py`](prompt.py)** | Defines the agent's `system_instruction` prompt. Details the simulator's role definition, simulation rules (15 flights, airline diversity, overnight formatting), input context placeholders, and output JSON specifications. |
| **[`schema.py`](schema.py)** | Defines Pydantic models for data validation and typing: `Filters`, `FlightsSearchInput`, `Flight`, and `FlightsSearchOutput`. |
| **[`env.yaml`](env.yaml)** | Configuration file containing Vertex AI / Google Cloud project settings and API credentials. |
| **[`requirements.txt`](requirements.txt)** | Python dependencies required by this service (e.g., `fastapi`, `uvicorn`, `google-adk`, `google-genai`, `pydantic`, `PyYAML`). |
| **[`__init__.py`](__init__.py)** | Marks the directory as a Python package. |

> **Note:** `main2.py` is an alternative experimental script and is not part of the standard production pipeline.

---

## 📊 Data Schemas

### Request Model: `FlightsSearchInput`
```json
{
  "origin": "Paris",
  "destination": "New York",
  "departure_date": "2026-05-10",
  "return_date": "2026-05-20",
  "passengers": 1,
  "filters": {
    "direct": false,
    "max_price": 800,
    "max_stops": 1
  }
}
```

### Response Model (Envelope)
```json
{
  "status": "success",
  "results": [
    {
      "flights": [
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
  ]
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
    "message": "Flights Search Agent Service is running. Use the /run-flights-search endpoint via POST."
  }
  ```

### 2. Run Flight Search
- **Method:** `POST`
- **Path:** `/run-flights-search`
- **Headers:** `Content-Type: application/json`
- **Body:** `FlightsSearchInput`
- **Example cURL:**
  ```bash
  curl -X POST "http://localhost:8006/run-flights-search" \
    -H "Content-Type: application/json" \
    -d '{
      "origin": "Paris",
      "destination": "New York",
      "departure_date": "2026-05-10",
      "return_date": "2026-05-20",
      "passengers": 1,
      "filters": {
        "max_price": 900,
        "max_stops": 1
      }
    }'
  ```

---

## 🚀 Running Locally

### 1. Prerequisites
- Python >= 3.11
- Vertex AI or Gemini API credentials configured in your environment or `env.yaml`.

### 2. Installation
From the repository root (`flights_search/`):
```bash
pip install -r agents/flights_search/requirements.txt
```

### 3. Start the Service
You can start the service directly using Python:
```bash
python -m agents.flights_search.main
```
Or via Uvicorn:
```bash
uvicorn agents.flights_search.main:api --host 127.0.0.1 --port 8006 --reload
```

---

## 🧪 Testing

Run the automated test suite using `pytest` or directly with Python from the root directory:

```bash
# Using pytest
pytest tests/flights_search/test.py

# Or running the test script directly
python -m tests.flights_search.test
```
