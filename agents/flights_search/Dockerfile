FROM python:3.11-slim

WORKDIR /app

# Copy the agent-specific requirements
COPY agents/flights_search/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy common utilities and the agent code
COPY utils/ ./utils/
COPY agents/flights_search/ ./agents/flights_search/

# Set execution path and run the agent
ENV PYTHONPATH=/app
ENV PORT=8080

CMD ["sh", "-c", "uvicorn agents.flights_search.main:api --host 0.0.0.0 --port $PORT"]
