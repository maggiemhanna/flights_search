# 🎯 Filter Agent Service

The **Filter Agent** is a specialized microservice built with **Google ADK (Agent Development Kit)** and **FastAPI**. It acts as a **Filter Extraction Agent**, translating user natural language queries into deterministic, programmatic parameters (`direct`, `max_price`, `max_stops`) for rule-based flight filtering.

---

## 🌟 How the Agent & Backend Work

### 1. The Agent Architecture (`Google ADK` + `Gemini 2.5 Pro`)
- **Role:** Translates natural language flight preferences into structured database query parameters. Rather than attempting to filter data directly (which risks hallucination), the agent extracts standard parameters so that deterministic backend logic can filter flights with 100% precision.
- **Model:** Powered by Google's `gemini-2.5-pro` through `google-adk`.
- **Extraction Rules & Supported Filter Types:**
  - **`direct`**:
    - **Triggers:** "non-stop", "direct", "no stops", "straight there".
    - **Value:** `1` (true) or `0` (false).
  - **`max_price`**:
    - **Triggers:** "under $X", "less than X", "cheapest", "my budget is X".
    - **Value:** Integer amount (e.g., `500`).
  - **`max_stops`**:
    - **Triggers:** "at most 1 stop", "maximum 2 stops", "no more than one stop".
    - **Value:** Integer count (e.g., `0`, `1`, `2`).
- **Context Handling:** Processes both the immediate `user_message` and full `conversational_history` to understand contextual refinements.
- **Data Contracts:** Input and output structures are validated using **Pydantic** models (`FilterInput` and `FilterOutput`).

### 2. The FastAPI Backend Architecture
- **Framework:** FastAPI with Uvicorn ASGI server.
- **Environment Setup:** Automatically loads environment variables from `env.yaml` on startup (Vertex AI project, region, etc.).
- **Per-Request Session Isolation:**
  - Generates unique per-request `session_id` and `user_id` using `uuid4()`.
  - Instantiates an `InMemorySessionService` populated with the initial request state (`user_message` and `conversational_history`).
  - An ADK `Runner` executes the agent with the prompt `"Follow the system instructions."` in debug mode.
  - The agent's structured response is extracted, JSON-parsed, and returned in a consistent response envelope.

---

## 📁 File Structure & Breakdown

| File | Purpose |
| :--- | :--- |
| **[`agent.py`](agent.py)** | Instantiates the Google ADK `Agent` (`filter_agent`) using `Gemini(model="gemini-2.5-pro")`, attaches system instructions, schemas, and registers the agent into an ADK `App`. |
| **[`main.py`](main.py)** | The core FastAPI backend application. Loads environment configurations, manages session lifecycle and runner execution, and exposes REST endpoints (`/` and `/run-filter`). Runs Uvicorn on port `8002` when executed directly. |
| **[`prompt.py`](prompt.py)** | Defines the agent's `system_instruction` prompt. Specifies role definitions, trigger rules for `direct`, `max_price`, and `max_stops`, few-shot extraction examples, input context placeholders, and JSON output formatting constraints. |
| **[`schema.py`](schema.py)** | Defines Pydantic models for data contracts: `FilterInput` and `FilterOutput`. |
| **[`env.yaml`](env.yaml)** | Configuration file containing Vertex AI / Google Cloud project settings and API flags. |
| **[`requirements.txt`](requirements.txt)** | Python dependencies required by this service (e.g., `fastapi`, `uvicorn`, `google-adk`, `google-genai`, `pydantic`, `PyYAML`). |
| **[`__init__.py`](__init__.py)** | Marks the directory as a Python package. |

---

## 📊 Data Schemas

### Request Model: `FilterInput`
```json
{
  "user_message": "Show me direct flights only under 500 euros",
  "conversational_history": [
    "user: Search flights from Paris to New York on 2026-05-10",
    "bot: Found 15 flights matching your criteria."
  ]
}
```

### Response Model: `FilterOutput` (Envelope)
```json
{
  "status": "success",
  "results": [
    {
      "filter_response": "Searching for direct flights only.",
      "filter_type": "direct",
      "filter_value": 1
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
    "message": "Filter Agent Service is running. Use the /run-filter endpoint via POST."
  }
  ```

### 2. Run Filter Extraction
- **Method:** `POST`
- **Path:** `/run-filter`
- **Headers:** `Content-Type: application/json`
- **Body:** `FilterInput`
- **Example cURL:**
  ```bash
  curl -X POST "http://localhost:8002/run-filter" \
    -H "Content-Type: application/json" \
    -d '{
      "user_message": "I want flights with at most 1 stop",
      "conversational_history": [
        "user: Looking for flights from London to Tokyo",
        "bot: Here are the available flights."
      ]
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
pip install -r agents/filter/requirements.txt
```

### 3. Start the Service
You can start the service directly using Python:
```bash
python -m agents.filter.main
```
Or via Uvicorn:
```bash
uvicorn agents.filter.main:api --host 127.0.0.1 --port 8002 --reload
```

---

## 🧪 Testing

Run the automated test suite using `pytest` or directly with Python from the root directory:

```bash
# Using pytest
pytest tests/filter/test.py

# Or running the test script directly
python -m tests.filter.test
```
