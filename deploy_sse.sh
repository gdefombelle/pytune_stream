#!/bin/bash
set -e

SERVICE_NAME="pytune_stream"
SERVER="root@195.201.9.184"

# Always build from repo root
REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

REMOTE_DIR="/root/deploy/$SERVICE_NAME"
LOGS_DIR="/root/pytune_logs/$SERVICE_NAME"

echo "🚀 Deploying $SERVICE_NAME to server…"

echo "📦 Building Docker image..."
docker build -t $SERVICE_NAME:latest \
    -f src/services/pytune_stream/Dockerfile \
    .

echo "📦 Saving image to tarball..."
docker save $SERVICE_NAME:latest | gzip > $SERVICE_NAME.tar.gz

echo "📤 Uploading to server..."
ssh $SERVER "mkdir -p $REMOTE_DIR"
scp $SERVICE_NAME.tar.gz $SERVER:$REMOTE_DIR/

echo "🔧 Deploying on server..."
ssh $SERVER << EOF
set -e

cd $REMOTE_DIR

gunzip -f $SERVICE_NAME.tar.gz
docker load < $SERVICE_NAME.tar

docker stop $SERVICE_NAME || true
docker rm $SERVICE_NAME || true

mkdir -p $LOGS_DIR

docker run -d \
    --name $SERVICE_NAME \
    --restart always \
    -p 8009:8009 \
    -v $LOGS_DIR:/var/log/pytune \
    -e LOG_DIR="/var/log/pytune" \
    $SERVICE_NAME:latest

rm -f $SERVICE_NAME.tar

EOF

echo "🎉 Done!"