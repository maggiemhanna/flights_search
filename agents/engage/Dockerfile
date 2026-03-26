FROM python:3.11-slim

WORKDIR /app

# Copy the agent-specific requirements
COPY agents/engage/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy common utilities and the agent code
COPY utils/ ./utils/
COPY agents/engage/ ./agents/engage/

# Set execution path and run the agent
ENV PYTHONPATH=/app
ENV PORT=8080

CMD ["sh", "-c", "uvicorn agents.engage.main:api --host 0.0.0.0 --port $PORT"]
