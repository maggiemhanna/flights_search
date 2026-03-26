FROM python:3.11-slim

WORKDIR /app

# Copy the agent-specific requirements
COPY agents/json_parser/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy common utilities and the agent code
COPY utils/ ./utils/
COPY agents/json_parser/ ./agents/json_parser/

# Set execution path and run the agent
ENV PYTHONPATH=/app
ENV PORT=8080

CMD ["sh", "-c", "uvicorn agents.json_parser.main:api --host 0.0.0.0 --port $PORT"]
