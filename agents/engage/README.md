# 🤝 Engage Agent Service

The **Engage Agent** is the triage and intent classification microservice built with **Google ADK (Agent Development Kit)** and **FastAPI**. It acts as the primary **Receptionist & Triage Specialist** for the conversational flight search system, analyzing user messages alongside conversation history to accurately route requests to the appropriate downstream specialized agent or continue the dialog.

---

## 🌟 How the Agent & Backend Work

### 1. The Agent Architecture (`Google ADK` + `Gemini 2.5 Pro`)
- **Role:** Evaluates user intent to determine the next conversational action and agent routing decision.
- **Model:** Powered by Google's `gemini-2.5-pro` through `google-adk`.
- **Hierarchical Routing Logic:**
  1. **`inspiration_agent` (Inspiration / Discovery):**
     - **Triggers:** Open-ended destination requests, broad regions, or vague timeframes (e.g., *"somewhere sunny in December"*, *"take me to Europe"*, *"ideas for skiing"*).
  2. **`filter` (Deterministic Hard Filters):**
     - **Triggers:** Narrowing down results using only hard parameters: `max_price` (*"under $500"*), `max_stops` (*"at most 1 stop"*), or `direct` (*"direct flights only"*).
  3. **`smart_filter` (Semantic & Soft Filters):**
     - **Triggers:** Preferences not covered by hard database filters, including specific airlines (*"Air France only"*), time-of-day (*"morning departures"*), aircraft types (*"A350"*), or amenities (*"high-speed WiFi"*, *"extra legroom"*).
  4. **`continue` (Engagement & Clarification):**
     - **Triggers:** Greetings (*"Hello"*), acknowledgments (*"Thanks"*), or ambiguous requests requiring follow-up questions formulated in `agent_response`.
- **Data Contracts:** Input and output structures are validated using **Pydantic** models (`EngageInput` and `EngageOutput`).

### 2. The FastAPI Backend Architecture
- **Framework:** FastAPI with Uvicorn ASGI server running on port `8001`.
- **Environment Setup:** Loads environment settings from `env.yaml` on startup (Vertex AI project, location, etc.).
- **Per-Request Session Isolation:**
  - Generates unique per-request `session_id` and `user_id` using `uuid4()`.
  - Instantiates an `InMemorySessionService` populated with the initial state (`user_message` and `conversational_history`).
  - An ADK `Runner` executes the agent with the prompt `"Follow the system instructions."` in debug mode.
  - The model's response parts are extracted and parsed into JSON.

---

## 📁 File Structure & Breakdown

| File | Purpose |
| :--- | :--- |
| **[`agent.py`](agent.py)** | Instantiates the Google ADK `Agent` (`engage`) using `Gemini(model="gemini-2.5-pro")`, attaches system instructions, schemas, and registers the agent into an ADK `App`. |
| **[`main.py`](main.py)** | The core FastAPI backend application. Manages environment configurations, session runners, JSON parsing, and exposes REST endpoints (`/` and `/run-engage`). Runs Uvicorn on port `8001` when executed directly. |
| **[`prompt.py`](prompt.py)** | Defines the agent's `system_instruction` prompt. Specifies triage role definitions, 4-step decision hierarchy, classification examples, and output formatting rules. |
| **[`schema.py`](schema.py)** | Defines Pydantic models for data contracts: `EngageInput` and `EngageOutput`. |
| **[`env.yaml`](env.yaml)** | Configuration file containing Vertex AI / Google Cloud project settings and API flags. |
| **[`requirements.txt`](requirements.txt)** | Python dependencies required by this service (e.g., `fastapi`, `uvicorn`, `google-adk`, `google-genai`, `pydantic`, `PyYAML`). |
| **[`Dockerfile`](Dockerfile)** | Container build definition based on `python:3.11-slim` for containerizing the service and running Uvicorn on port `8080` (or dynamic `$PORT`). |
| **[`cloudbuild.yaml`](cloudbuild.yaml)** | Google Cloud Build pipeline specification to build the container, push to Google Container Registry (GCR), and deploy to Google Cloud Run in `europe-west9`. |
| **[`__init__.py`](__init__.py)** | Marks the directory as a Python package. |

---

## 📊 Data Schemas

### Request Model: `EngageInput`
```json
{
  "user_message": "I only want direct flights under 600 euros.",
  "conversational_history": [
    "user: Search flights from Paris to New York on 2026-05-10",
    "bot: Found 15 flights matching your search."
  ]
}
```

### Response Model: `EngageOutput` (Envelope)
```json
{
  "status": "success",
  "results": [
    {
      "agent_response": "Filtering for direct flights under 600 EUR.",
      "agent_decision": "filter"
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
    "message": "Engage Agent Service is running. Use the /run-engage endpoint via POST."
  }
  ```

### 2. Run Intent Engagement
- **Method:** `POST`
- **Path:** `/run-engage`
- **Headers:** `Content-Type: application/json`
- **Body:** `EngageInput`
- **Example cURL:**
  ```bash
  curl -X POST "http://localhost:8001/run-engage" \
    -H "Content-Type: application/json" \
    -d '{
      "user_message": "Can you recommend a sunny vacation in July?",
      "conversational_history": []
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
pip install -r agents/engage/requirements.txt
```

### 3. Start the Service
You can start the service directly using Python:
```bash
python -m agents.engage.main
```
Or via Uvicorn:
```bash
uvicorn agents.engage.main:api --host 127.0.0.1 --port 8001 --reload
```

---

## 🧪 Testing

Run the automated test suite using `pytest` or directly with Python from the root directory:

```bash
# Using pytest
pytest tests/engage/test.py

# Or running the test script directly
python -m tests.engage.test
```

---

## 🐳 Deployment (Docker & Cloud Run)

### Local Docker Run
```bash
# Build from project root
docker build -t engage-service -f agents/engage/Dockerfile .

# Run container
docker run -p 8001:8080 -e PORT=8080 engage-service
```

### Google Cloud Run Deployment
Using Google Cloud Build (`cloudbuild.yaml`):
```bash
gcloud builds submit --config=agents/engage/cloudbuild.yaml .
```
Deploys to Cloud Run with:
- **Region:** `europe-west9`
- **Memory:** `2Gi`
- **CPU:** `2`
- **Min Instances:** `1` (no CPU throttling)
