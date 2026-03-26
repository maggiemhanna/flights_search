#!/bin/bash

# Explicitly set the project for Google Cloud CLI
export PROJECT_ID="vertexai-explore-437408"
export CLOUDSDK_CORE_PROJECT="$PROJECT_ID"
export SERVICE_ACCOUNT="874751466618-compute@developer.gserviceaccount.com"

echo "Deploying the React frontend to project $PROJECT_ID..."

# Submit build and deploy to Cloud Run using the configuration
gcloud builds submit --config "frontend/cloudbuild.yaml" .

if [ $? -eq 0 ]; then
  echo "✅ Frontend deployed successfully!"
else
  echo "⚠️ Frontend deployment failed."
  exit 1
fi
