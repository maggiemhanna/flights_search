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

echo "Deploying the React frontend to project $PROJECT_ID..."

# Submit build and deploy to Cloud Run using the configuration
gcloud builds submit --config "frontend/cloudbuild.yaml" .

if [ $? -eq 0 ]; then
  echo "✅ Frontend deployed successfully!"
else
  echo "⚠️ Frontend deployment failed."
  exit 1
fi
