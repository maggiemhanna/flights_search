#!/bin/bash

# Explicitly set the project for Google Cloud CLI
export PROJECT_ID="vertexai-explore-437408"
export SERVICE_ACCOUNT="874751466618-compute@developer.gserviceaccount.com"
export CLOUDSDK_CORE_PROJECT="$PROJECT_ID"
export AGENT_NAME="flights_search"

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

echo "Deploying microservice to project $PROJECT_ID..."

# Define the agents to deploy
AGENTS=($AGENT_NAME)

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