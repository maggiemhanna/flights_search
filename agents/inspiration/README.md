# 💡 Inspiration Agent Service

The **Inspiration Agent** is an exploratory microservice built with **Google ADK (Agent Development Kit)** and **FastAPI**. It acts as a **Travel Discovery Architect**, analyzing open-ended or ambiguous travel desires (e.g., *"I want to travel somewhere sunny in December"*, *"Find me a trip to Europe in May"*) and dynamically translating them into concrete, searchable flight parameters (origin, destination, dates, passengers) accompanied by an engaging travel pitch.

---

## 🌟 How the Agent & Backend Work

### 1. The Agent Architecture (`Google ADK` + `Gemini 2.5 Pro`)
- **Role:** Transforms vague travel aspirations and seasonal themes into concrete search parameters.
- **Model:** Powered by Google's `gemini-2.5-pro` through `google-adk`.
- **Discovery & Selection Logic:**
  - **Intent Analysis:** Identifies whether the user is seeking a new destination, a shifted timeframe/season, or both.
  - **Themes to Destinations:** Maps themes (e.g., "sunny beaches", "ski vacation", "romantic getaway") to top real-world destinations aligned with seasonal trends.
  - **Regions to Major Hubs:** Resolves broad regions (e.g., "Europe", "Southeast Asia", "The Mediterranean") to major international flight hubs (e.g., London, Paris, Bangkok, Barcelona).
  - **Date Resolution:** Converts seasonal phrases (e.g., "next month", "in June", "autumn getaway") into concrete `YYYY-MM-DD` departure and return dates.
  - **Context Persistence:** Retains existing traveler origin and passenger count unless the user explicitly requests changes.
  - **Inspiration Pitch:** Generates a tailored `inspiration_response` explaining why the proposed destination and dates fit the user's travel vibe.
- **Data Contracts:** Input and output structures are validated using **Pydantic** models (`InspirationInput` and `InspirationOutput`).

### 2. The FastAPI Backend Architecture
- **Framework:** FastAPI with Uvicorn ASGI server running on port `8007`.
- **Environment Setup:** Loads environment settings from `env.yaml` on startup (Vertex AI project, location, etc.).
- **Per-Request Session Isolation:**
  - Generates unique per-request `session_id` and `user_id` using `uuid4()`.
  - Instantiates an `InMemorySessionService` populated with the initial search parameters, user message, and chat history.
  - An ADK `Runner` executes the agent with `"Follow the system instructions."` in debug mode.
  - Model responses are JSON-parsed and returned in a unified response envelope.

---

## 📁 File Structure & Breakdown

| File | Purpose |
| :--- | :--- |
| **[`agent.py`](agent.py)** | Instantiates the Google ADK `Agent` (`inspiration`) using `Gemini(model="gemini-2.5-pro")`, attaches system instructions, schemas, and registers the agent into an ADK `App`. |
| **[`main.py`](main.py)** | The core FastAPI backend application. Manages environment configurations, session runners, JSON parsing, and exposes REST endpoints (`/` and `/run-inspiration`). Runs Uvicorn on port `8007` when executed directly. |
| **[`prompt.py`](prompt.py)** | Defines the agent's `system_instruction` prompt. Specifies role definitions, task guidelines (theme mapping, region resolution, date synthesis), logic examples, and output formatting rules. |
| **[`schema.py`](schema.py)** | Defines Pydantic models for data contracts: `InspirationInput` and `InspirationOutput`. |
| **[`env.yaml`](env.yaml)** | Configuration file containing Vertex AI / Google Cloud project settings and API flags. |
| **[`requirements.txt`](requirements.txt)** | Python dependencies required by this service (e.g., `fastapi`, `uvicorn`, `google-adk`, `google-genai`, `pydantic`, `PyYAML`). |
| **[`Dockerfile`](Dockerfile)** | Container build definition based on `python:3.11-slim` for containerizing the service and running Uvicorn on port `8080` (or dynamic `$PORT`). |
| **[`cloudbuild.yaml`](cloudbuild.yaml)** | Google Cloud Build pipeline specification to build the container, push to Google Container Registry (GCR), and deploy to Google Cloud Run in `europe-west9`. |
| **[`__init__.py`](__init__.py)** | Marks the directory as a Python package. |

---

## 📊 Data Schemas

### Request Model: `InspirationInput`
```json
{
  "origin": "Paris",
  "destination": "New York",
  "departure_date": "2026-05-10",
  "return_date": "2026-05-20",
  "passengers": 1,
  "user_message": "I want to go somewhere sunny and warm in December instead.",
  "conversational_history": [
    "user: Search flights from Paris to New York",
    "bot: Here are 15 flights found."
  ]
}
```

### Response Model: `InspirationOutput` (Envelope)
```json
{
  "status": "success",
  "results": [
    {
      "origin": "Paris",
      "destination": "Cancun",
      "departure_date": "2026-12-05",
      "return_date": "2026-12-15",
      "passengers": 1,
      "inspiration_response": "How about swapping the chilly winter for tropical beaches in Cancun? December is prime season for warm weather and clear skies in the Caribbean!"
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
    "message": "Inspiration Agent Service is running. Use the /run-inspiration endpoint via POST."
  }
  ```

### 2. Run Inspiration Search
- **Method:** `POST`
- **Path:** `/run-inspiration`
- **Headers:** `Content-Type: application/json`
- **Body:** `InspirationInput`
- **Example cURL:**
  ```bash
  curl -X POST "http://localhost:8007/run-inspiration" \
    -H "Content-Type: application/json" \
    -d '{
      "origin": "London",
      "destination": "Paris",
      "departure_date": "2026-06-01",
      "return_date": "2026-06-10",
      "passengers": 2,
      "user_message": "Take us somewhere in Southern Europe with great food and history.",
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
pip install -r agents/inspiration/requirements.txt
```

### 3. Start the Service
You can start the service directly using Python:
```bash
python -m agents.inspiration.main
```
Or via Uvicorn:
```bash
uvicorn agents.inspiration.main:api --host 127.0.0.1 --port 8007 --reload
```

---

## 🧪 Testing

Run the automated test suite using `pytest` or directly with Python from the root directory:

```bash
# Using pytest
pytest tests/inspiration/test.py

# Or running the test script directly
python -m tests.inspiration.test
```

---

## 🐳 Deployment (Docker & Cloud Run)

### Local Docker Run
```bash
# Build from project root
docker build -t inspiration-service -f agents/inspiration/Dockerfile .

# Run container
docker run -p 8007:8080 -e PORT=8080 inspiration-service
```

### Google Cloud Run Deployment
Using Google Cloud Build (`cloudbuild.yaml`):
```bash
gcloud builds submit --config=agents/inspiration/cloudbuild.yaml .
```
Deploys to Cloud Run with:
- **Region:** `europe-west9`
- **Memory:** `2Gi`
- **CPU:** `2`
- **Min Instances:** `1` (no CPU throttling)
