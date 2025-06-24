#!/bin/bash
set -e

# --- Configuration ---
# These variables should be filled in with your project's details
PROJECT_ID="copper-sunspot-462216-j2"
REGION="africa-south1"
SERVICE_NAME="frisque-celery-worker"
CLOUD_SQL_CONNECTION="copper-sunspot-462216-j2:africa-south1:frisque-db-prod"
DB_USER="frisque_prod_user"
DB_NAME="frisque_prod"
CELERY_BROKER_URL="amqps://subyftcp:ctYdBObrDIZgS4wCV10uOU0s4LM8hnFd@kangaroo.rmq.cloudamqp.com/subyftcp"


echo "🚀 Deploying Celery Worker to Cloud Run..."

gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --command "celery" \
  --args="-A" \
  --args="frisque_core" \
  --args="worker" \
  --args="-l" \
  --args="info" \
  --no-cpu-throttling \
  --set-cloudsql-instances "$CLOUD_SQL_CONNECTION" \
  --set-env-vars="POSTGRES_USER=$DB_USER,POSTGRES_NAME=$DB_NAME,CLOUD_SQL_INSTANCE_CONNECTION_NAME=$CLOUD_SQL_CONNECTION,CELERY_BROKER_URL=$CELERY_BROKER_URL" \
  --set-secrets="POSTGRES_PASSWORD=PROD_DB_PASSWORD:latest,DJANGO_SECRET_KEY=DJANGO_SECRET_KEY:latest"

echo "🎉 Celery Worker deployed successfully!"
