#!/bin/bash
set -e  # exit on any error

REPO=307946642170.dkr.ecr.eu-north-1.amazonaws.com/social-media-backend
TAG=latest  # or dynamic: TAG=$(date +%Y%m%d%H%M%S)

echo "Building Docker image..."
docker build --platform linux/amd64 -t $REPO:$TAG .

echo "Logging into ECR..."
aws ecr get-login-password --region eu-north-1 --profile personal \
  | docker login --username AWS --password-stdin $REPO

echo "Pushing Docker image..."
docker push $REPO:$TAG

echo "✅ Deployment image pushed successfully!"
