# 🧠 Smart Filter Agent Service

The **Smart Filter Agent** is an advanced microservice built with **Google ADK (Agent Development Kit)** and **FastAPI**. It acts as a **Smart-Filter Flight Specialist**, performing semantic analysis and live web research on flight search results to handle complex, qualitative, or "soft" traveler preferences (e.g., fast WiFi, extra legroom, preferred aircraft types, or time-of-day requests) that rigid database filters cannot process.

---

## 🌟 How the Agent & Backend Work

### 1. The Agent Architecture (`Google ADK` + `Gemini 2.5 Pro` + `Google Search`)
- **Role:** Evaluates soft and qualitative constraints across a list of candidate flights. It combines structured reasoning over flight metadata with live external web research to determine which flights best meet the user's nuanced requirements.
- **Model & Tools:** Powered by Google's `gemini-2.5-pro` with access to the `google_search` tool (`tools=[google_search]`) for live amenity and airline verification.
- **Multi-Stage Task Logic:**
  1. **Constraint Identification:** Distinguishes between *explicit constraints* (specific airlines, departure times like "morning = 06:00-12:00", specific airports) and *soft/implicit constraints* (high-speed WiFi, seat pitch, modern aircraft, good food).
  2. **Primary Filtering (Internal Data):** Filters candidate flights against explicit metadata criteria.
  3. **Secondary Filtering (Live Web Research):** Dynamically invokes Google Search to query amenity details (e.g., *"Does Delta flight DL123 have high-speed Viasat WiFi?"* or *"Boeing 787-9 seat pitch Air France"*).
  4. **Final Refinement & Explanation:** Assembles qualifying flights, preserves intact flight objects (no mutation of IDs, flight numbers, or pricing), and writes a detailed 2+ sentence `filter_response` explaining what was filtered, researched, and kept.
- **Data Contracts:** Input and output structures are validated using **Pydantic** models (`FilterSmartInput` and `FilterSmartOutput`).

### 2. The FastAPI Backend Architecture
- **Framework:** FastAPI with Uvicorn ASGI server running on port `8003`.
- **Environment Setup:** Loads environment settings from `env.yaml` on startup (Vertex AI project, location, etc ...).
- **Per-Request Session Isolation:**
  - Generates unique per-request `session_id` and `user_id` using `uuid4()`.
  - Instantiates an `InMemorySessionService` populated with the initial state (`user_message`, `conversational_history`, and `flights_input`).
  - An ADK `Runner` executes the agent with `"Follow the system instructions."` in debug mode.
- **Resilient JSON Parsing & Self-Healing:**
  - Extracts and strips markdown fence blocks via regex (`load_json_with_markdown`).
  - Includes a fallback integration with the **JSON Parser Microservice** (`call_json_parser_api`) if an LLM response fails raw JSON parsing.

---

## 📁 File Structure & Breakdown

| File | Purpose |
| :--- | :--- |
| **[`agent.py`](agent.py)** | Instantiates the primary Google ADK `Agent` (`filter_smart_agent`) with `Gemini(model="gemini-2.5-pro")`, connects the `google_search` tool, binds system prompts and input schemas, and wraps it in an ADK `App`. |
| **[`main.py`](main.py)** | The core FastAPI backend application. Manages environment configurations, session runners, markdown/JSON parsing, JSON Parser fallback recovery, and exposes REST endpoints (`/` and `/run-filter-smart`). Runs Uvicorn on port `8003` when executed directly. |
| **[`prompt.py`](prompt.py)** | Defines the agent's `system_instruction` prompt. Specifies role definitions, multi-stage task logic flows, Google Search query protocols, time definitions, and output JSON schema constraints. |
| **[`schema.py`](schema.py)** | Defines Pydantic models for data validation: `Flight`, `FilterSmartInput`, and `FilterSmartOutput`. |
| **[`env.yaml`](env.yaml)** | Configuration file containing Vertex AI / Google Cloud project settings, Google CSE ID, and API keys. |
| **[`requirements.txt`](requirements.txt)** | Python dependencies required by this service (e.g., `fastapi`, `uvicorn`, `google-adk`, `google-genai`, `pydantic`). |
| **[`Dockerfile`](Dockerfile)** | Container build definition based on `python:3.11-slim` for containerizing the service and running Uvicorn on port `8080` (or dynamic `$PORT`). |
| **[`cloudbuild.yaml`](cloudbuild.yaml)** | Google Cloud Build pipeline specification to build the container, push to Google Container Registry (GCR), and deploy to Google Cloud Run in `europe-west9`. |
| **[`__init__.py`](__init__.py)** | Marks the directory as a Python package. |

---

## 📊 Data Schemas

### Request Model: `FilterSmartInput`
```json
{
  "user_message": "I only want flights that have good WiFi and depart in the morning.",
  "conversational_history": [
    "user: Search flights from London to New York on 2026-05-10",
    "bot: Found 15 flights matching your search."
  ],
  "flights_input": [
    {
      "origin": "London (LHR)",
      "destination": "New York (JFK)",
      "departure_date": "2026-05-10",
      "return_date": "2026-05-20",
      "departure_time": "09:30",
      "arrival_time": "12:15",
      "return_time": "18:00",
      "return_arrival_time": "06:20 +1",
      "price": "610 EUR",
      "airline": "British Airways",
      "flight_number": "BA178",
      "stops": 0,
      "stopover_cities": []
    }
  ]
}
```

### Response Model: `FilterSmartOutput` (Envelope)
```json
{
  "status": "success",
  "results": [
    {
      "filter_response": "Filtered out afternoon flights to match your morning preference (06:00-12:00). Researched in-flight connectivity and confirmed British Airways BA178 offers high-speed satellite WiFi.",
      "flights_output": [
        {
          "origin": "London (LHR)",
          "destination": "New York (JFK)",
          "departure_date": "2026-05-10",
          "return_date": "2026-05-20",
          "departure_time": "09:30",
          "arrival_time": "12:15",
          "return_time": "18:00",
          "return_arrival_time": "06:20 +1",
          "price": "610 EUR",
          "airline": "British Airways",
          "flight_number": "BA178",
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
    "message": "Filter Smart Agent Service is running. Use the /run-filter-smart endpoint via POST."
  }
  ```

### 2. Run Smart Filter
- **Method:** `POST`
- **Path:** `/run-filter-smart`
- **Headers:** `Content-Type: application/json`
- **Body:** `FilterSmartInput`
- **Example cURL:**
  ```bash
  curl -X POST "http://localhost:8003/run-filter-smart" \
    -H "Content-Type: application/json" \
    -d '{
      "user_message": "Show only morning flights with good legroom",
      "conversational_history": [],
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
    }'
  ```

---

## 🚀 Running Locally

### 1. Prerequisites
- Python >= 3.11
- Vertex AI and Google Search credentials configured in your environment or `env.yaml`.

### 2. Installation
From the repository root (`flights_search/`):
```bash
pip install -r agents/filter_smart/requirements.txt
```

### 3. Start the Service
You can start the service directly using Python:
```bash
python -m agents.filter_smart.main
```
Or via Uvicorn:
```bash
uvicorn agents.filter_smart.main:api --host 127.0.0.1 --port 8003 --reload
```

---

## 🧪 Testing

Run the automated test suite using `pytest` or directly with Python from the root directory:

```bash
# Using pytest
pytest tests/filter_smart/test.py

# Or running the test script directly
python -m tests.filter_smart.test
```

---

## 🐳 Deployment (Docker & Cloud Run)

### Local Docker Run
```bash
# Build from project root
docker build -t filter-smart-service -f agents/filter_smart/Dockerfile .

# Run container
docker run -p 8003:8080 -e PORT=8080 filter-smart-service
```

### Google Cloud Run Deployment
Using Google Cloud Build (`cloudbuild.yaml`):
```bash
gcloud builds submit --config=agents/filter_smart/cloudbuild.yaml .
```
Deploys to Cloud Run with:
- **Region:** `europe-west9`
- **Memory:** `2Gi`
- **CPU:** `2`
- **Min Instances:** `1` (no CPU throttling)
