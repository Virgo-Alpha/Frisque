#!/bin/bash

set -e

# Configuration
PROJECT_ID="copper-sunspot-462216-j2"
REGION="africa-south1"
SERVICE_NAME="frisque-web-app"
REPO_NAME="frisque-repo"
CLOUD_SQL_CONNECTION="copper-sunspot-462216-j2:africa-south1:frisque-db-prod"
DB_USER="frisque_prod_user"
DB_NAME="frisque_prod"
APP_DOMAIN=$(gcloud run services describe "$SERVICE_NAME" --platform managed --region "$REGION" --format 'value(status.url)' | sed 's|https://||')

# Full image name in Artifact Registry
IMAGE_NAME="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$SERVICE_NAME"

echo "🚀 Building Docker image..."
docker build -t "$IMAGE_NAME" -f Dockerfile.prod .

echo "🔐 Configuring docker to authenticate with Artifact Registry..."
gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet

echo "📦 Pushing image to Artifact Registry..."
docker push "$IMAGE_NAME"

echo "🚀 Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE_NAME" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --allow-unauthenticated \
  --add-cloudsql-instances "$CLOUD_SQL_CONNECTION" \
  --set-env-vars "POSTGRES_USER=$DB_USER" \
  --set-env-vars "POSTGRES_NAME=$DB_NAME" \
  --set-env-vars "CLOUD_SQL_INSTANCE_CONNECTION_NAME=$CLOUD_SQL_CONNECTION" \
  --set-secrets "POSTGRES_PASSWORD=PROD_DB_PASSWORD:latest" \
  --set-secrets "DJANGO_SECRET_KEY=DJANGO_SECRET_KEY:latest"

echo "✅ Deployment sent. Now running migrations..."

# Job 1: Apply migrations
gcloud beta run jobs create frisque-migrate \
  --image africa-south1-docker.pkg.dev/copper-sunspot-462216-j2/frisque-repo/frisque-web-app:latest \
  --command python3 \
  --args manage.py,migrate,--verbosity=3 \
  --set-secrets=POSTGRES_PASSWORD=PROD_DB_PASSWORD:latest,DJANGO_SECRET_KEY=DJANGO_SECRET_KEY:latest \
  --set-env-vars "POSTGRES_USER=frisque_prod_user,POSTGRES_NAME=frisque_prod,CLOUD_SQL_INSTANCE_CONNECTION_NAME=copper-sunspot-462216-j2:africa-south1:frisque-db-prod,APP_URL=$APP_DOMAIN"\
  --set-cloudsql-instances=copper-sunspot-462216-j2:africa-south1:frisque-db-prod \
  --region africa-south1

gcloud beta run jobs execute frisque-migrate --region africa-south1


# Job 2: Ensure the site exists
gcloud beta run jobs create frisque-ensure-site \
  --image africa-south1-docker.pkg.dev/copper-sunspot-462216-j2/frisque-repo/frisque-web-app:latest \
  --command python3 \
  --args manage.py,runscript,ensure_site \
  --set-secrets=POSTGRES_PASSWORD=PROD_DB_PASSWORD:latest,DJANGO_SECRET_KEY=DJANGO_SECRET_KEY:latest \
  --set-env-vars POSTGRES_USER=frisque_prod_user,POSTGRES_NAME=frisque_prod,CLOUD_SQL_INSTANCE_CONNECTION_NAME=copper-sunspot-462216-j2:africa-south1:frisque-db-prod \
  --set-cloudsql-instances=copper-sunspot-462216-j2:africa-south1:frisque-db-prod \
  --region africa-south1

gcloud beta run jobs execute frisque-ensure-site --region africa-south1

echo "🎉 Done!"
