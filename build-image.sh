#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Print commands before executing them
set -x

# Define variables
IMAGE_NAME="file-analyzer"
IMAGE_TAG="latest"
REGISTRY="registry.gitlab.com/nceriello/containers"
REMOTE_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

# Build the Docker image
echo "Building Docker image: ${REMOTE_IMAGE_NAME}"
docker build -t ${REMOTE_IMAGE_NAME} .

echo "Pushing Docker image to ${REGISTRY}"
docker push ${REMOTE_IMAGE_NAME}

echo "Done! Image pushed to ${REMOTE_IMAGE_NAME}"

# Print instructions for running the Docker container
cat << EOF

==========================================================
INSTRUCTIONS FOR RUNNING THE DOCKER CONTAINER
==========================================================

To run the Docker container locally:

  docker run -p 5000:5000 ${REMOTE_IMAGE_NAME}

To run the container from the registry:

  docker run -p 5000:5000 ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

Access the application at: http://localhost:5000

To mount a local directory for persistent uploads:

  docker run -p 5000:5000 -v /path/to/local/dir:/app/uploads ${REMOTE_IMAGE_NAME}

For production deployment with a proper WSGI server:

  docker run -p 5000:5000 -e FLASK_ENV=production ${REMOTE_IMAGE_NAME} gunicorn --bind 0.0.0.0:5000 app:app
==========================================================
EOF