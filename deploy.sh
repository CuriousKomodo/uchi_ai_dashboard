#!/bin/bash

# Uchi AI Dashboard - Cloud Run Deployment Script
set -e

# Configuration
PROJECT_ID="uchiai"
SERVICE_NAME="uchi-dashboard"
REGION="europe-west1"
REGISTRY="uchi-dashboard"
IMAGE_NAME="$REGION-docker.pkg.dev/$PROJECT_ID/$REGISTRY/$SERVICE_NAME"

echo "🚀 Deploying Uchi AI Dashboard to Cloud Run"

# Set project
gcloud config set project $PROJECT_ID

# Configure Docker for Artifact Registry
gcloud auth configure-docker $REGION-docker.pkg.dev

# Build and push image
echo "🔨 Building and pushing image..."
docker buildx build \
  --platform linux/amd64 \
  -t "$IMAGE_NAME" \
  --push \
  .

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo "✅ Deployment successful!"
echo "🌐 Your app is available at: $SERVICE_URL" 