#!/bin/bash

# Check if root env.yaml exists
if [ ! -f "env.yaml" ]; then
  echo "❌ Error: env.yaml not found in root directory."
  exit 1
fi

# Read PROJECT_ID and SERVICE_ACCOUNT from env.yaml
export PROJECT_ID=$(awk -F': ' '/PROJECT_ID:/ {gsub(/[" '\''\r]/, "", $2); print $2}' env.yaml)
export SERVICE_ACCOUNT=$(awk -F': ' '/SERVICE_ACCOUNT:/ {gsub(/[" '\''\r]/, "", $2); print $2}' env.yaml)

if [ -z "$PROJECT_ID" ] || [ -z "$SERVICE_ACCOUNT" ]; then
  echo "❌ Error: PROJECT_ID or SERVICE_ACCOUNT not found in env.yaml"
  exit 1
fi

export CLOUDSDK_CORE_PROJECT="$PROJECT_ID"

echo "Granting necessary IAM permissions to $SERVICE_ACCOUNT..."

# Array of roles to be assigned
ROLES=(
  "roles/artifactregistry.createOnPushWriter"
  "roles/logging.logWriter"
  "roles/run.admin"
  "roles/iam.serviceAccountUser"
)

for ROLE in "${ROLES[@]}"; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="$ROLE" --quiet > /dev/null
done

echo "Deploying microservices in parallel to project $PROJECT_ID..."

# Define the agents to deploy
AGENTS=("engage" "filter" "filter_smart" "json_parser" "orchestrator" "flights_search" "inspiration")

PIDS=()

# Submit builds in the background
for AGENT in "${AGENTS[@]}"; do
  gcloud builds submit --config "agents/$AGENT/cloudbuild.yaml" . &
  PIDS+=($!)
done

FAIL=0

# Wait for each process separately to catch any failures
for i in "${!AGENTS[@]}"; do
  wait "${PIDS[$i]}" || { echo "❌ ${AGENTS[$i]} deployment failed"; FAIL=1; }
done

# Check final failure status
if [ $FAIL -ne 0 ]; then
  echo "⚠️ One or more deployments failed."
  exit 1
else
  echo "✅ All microservices deployed successfully!"
fi