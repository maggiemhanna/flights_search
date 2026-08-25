# 🛠️ JSON Parser Agent Service

The **JSON Parser Agent** is a specialized structural assistant microservice built with **Google ADK (Agent Development Kit)** and **FastAPI**. It acts as a **JSON Corrector Specialist**, repairing malformed or invalid JSON payloads and ensuring strict structural compliance across the multi-agent system.

---

## 🌟 How the Agent & Backend Work

### 1. The Agent Architecture (`Google ADK` + `Gemini 2.5 Pro`)
- **Role:** Takes unformatted, broken, or syntactically invalid text output from other agents (e.g., `filter_smart`) and transforms it into clean, validated JSON adhering to strict Pydantic models.
- **Model:** Powered by Google's `gemini-2.5-pro` through `google-adk`.
- **Task Hierarchy & Correction Rules:**
  1. **Analyze Input:** Scans the incoming raw `response_text` for syntax errors, markdown backticks, mixed natural language, or unescaped characters.
  2. **Extract Data:** Separates the human-facing explanation (`filter_response`) from the flight listings (`flights_output`).
  3. **Fix JSON Structure:** Repairs common JSON syntax issues (missing quotes, unclosed brackets, trailing commas).
  4. **Validate Schema:** Enforces the target output schema with exact key definitions and data types.
  5. **Text Refinement:** Cleans up minor typos or awkward formatting in the natural language summary without altering the factual meaning.
- **Data Integrity Constraints:**
  - Strictly preserves existing flight details (e.g., flight numbers, prices, timestamps, origins/destinations).
  - Never invents flights or hallucinates missing attributes.
- **Data Contracts:** Input and output structures are validated using **Pydantic** models (`JSONParserInput` and `JSONParserOutput`).

### 2. The FastAPI Backend Architecture
- **Framework:** FastAPI with Uvicorn ASGI server running on port `8004`.
- **Environment Setup:** Loads environment settings from `env.yaml` on startup (Vertex AI project, location, etc.).
- **Per-Request Session Isolation:**
  - Generates unique per-request `session_id` and `user_id` using `uuid4()`.
  - Instantiates an `InMemorySessionService` populated with the initial request state (`response_text`).
  - An ADK `Runner` executes the agent with the prompt `"Follow the system instructions."` in debug mode.
  - The model's response parts are extracted and parsed into JSON.

---

## 📁 File Structure & Breakdown

| File | Purpose |
| :--- | :--- |
| **[`agent.py`](agent.py)** | Instantiates the Google ADK `Agent` (`json_parser_agent`) using `Gemini(model="gemini-2.5-pro")`, attaches system instructions, schemas, and registers the agent into an ADK `App`. |
| **[`main.py`](main.py)** | The core FastAPI backend application. Manages environment configurations, session runners, JSON parsing, and exposes REST endpoints (`/` and `/run-json-parser`). Runs Uvicorn on port `8004` when executed directly. |
| **[`prompt.py`](prompt.py)** | Defines the agent's `system_instruction` prompt. Specifies the 5-step task hierarchy, data integrity constraints, schema requirements, and pure JSON output formatting instructions. |
| **[`schema.py`](schema.py)** | Defines Pydantic models for data contracts: `Flight`, `JSONParserInput`, and `JSONParserOutput`. |
| **[`env.yaml`](env.yaml)** | Configuration file containing Vertex AI / Google Cloud project settings and API flags. |
| **[`requirements.txt`](requirements.txt)** | Python dependencies required by this service (e.g., `fastapi`, `uvicorn`, `google-adk`, `google-genai`, `pydantic`, `PyYAML`). |
| **[`__init__.py`](__init__.py)** | Marks the directory as a Python package. |

---

## 📊 Data Schemas

### Request Model: `JSONParserInput`
```json
{
  "response_text": "Here are the flights filtered for WiFi:\n{\n  'filter_response': 'Filtered for high-speed WiFi.',\n  'flights_output': [{\n    'origin': 'Paris (CDG)',\n    'destination': 'New York (JFK)',\n    'departure_date': '2026-05-10',\n    'return_date': '2026-05-20',\n    'departure_time': '10:30',\n    'arrival_time': '13:00',\n    'return_time': '17:30',\n    'return_arrival_time': '06:45 +1',\n    'price': '520 EUR',\n    'airline': 'Air France',\n    'flight_number': 'AF006',\n    'stops': 0,\n    'stopover_cities': []\n  }]\n}"
}
```

### Response Model: `JSONParserOutput` (Envelope)
```json
{
  "status": "success",
  "results": [
    {
      "filter_response": "Filtered for high-speed WiFi.",
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
    "message": "JSON Parser Agent Service is running. Use the /run-json-parser endpoint via POST."
  }
  ```

### 2. Run JSON Parser
- **Method:** `POST`
- **Path:** `/run-json-parser`
- **Headers:** `Content-Type: application/json`
- **Body:** `JSONParserInput`
- **Example cURL:**
  ```bash
  curl -X POST "http://localhost:8004/run-json-parser" \
    -H "Content-Type: application/json" \
    -d '{
      "response_text": "{\n  \"filter_response\": \"Showing direct flights only.\",\n  \"flights_output\": []\n}"
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
pip install -r agents/json_parser/requirements.txt
```

### 3. Start the Service
You can start the service directly using Python:
```bash
python -m agents.json_parser.main
```
Or via Uvicorn:
```bash
uvicorn agents.json_parser.main:api --host 127.0.0.1 --port 8004 --reload
```

---

## 🧪 Testing

Run the automated test suite using `pytest` or directly with Python from the root directory:

```bash
# Using pytest
pytest tests/json_parser/test.py

# Or running the test script directly
python -m tests.json_parser.test
```
