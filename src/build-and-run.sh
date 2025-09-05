#!/bin/bash

# Build and run the complete working Docker container for 3D PCD segmentation
# This script sets up the entire environment with all dependencies

set -e  # Exit on any error

echo "🚀 Starting 3D Point Cloud Segmentation Environment Setup..."
echo ""

# Check if supervisely.env exists
if [ ! -f "supervisely.env" ]; then
    echo "⚠️  Creating default supervisely.env file..."
    cat > supervisely.env << EOF
API_TOKEN=your_supervisely_token_here
SERVER_ADDRESS=https://app.supervisely.com
EOF
    echo "✅ Please edit supervisely.env with your actual Supervisely credentials"
fi

echo "🔨 Building Docker image with all dependencies..."
docker build -f .devcontainer/Dockerfile.complete-working -t pcd-segmentation-complete .

echo "🧹 Cleaning up existing containers..."
# Stop and remove existing containers gracefully
docker stop pcd-jupyter 2>/dev/null || true
docker rm pcd-jupyter 2>/dev/null || true

# Stop any containers using the same image
EXISTING_CONTAINERS=$(docker ps -q --filter "ancestor=pcd-segmentation-complete" 2>/dev/null || true)
if [ ! -z "$EXISTING_CONTAINERS" ]; then
    echo "Stopping existing containers..."
    docker stop $EXISTING_CONTAINERS 2>/dev/null || true
fi

echo "🚀 Starting new container..."
docker run -d -p 8888:8888 \
    -v $(pwd):/workspace \
    --env-file supervisely.env \
    --name pcd-jupyter \
    --restart unless-stopped \
    pcd-segmentation-complete

# Wait a moment for container to start
sleep 3

# Check if container is running
if docker ps | grep -q pcd-jupyter; then
    echo ""
    echo "✅ Container started successfully!"
    echo ""
    echo "🌐 Access Jupyter Notebook:"
    echo "   http://127.0.0.1:8888/?token=mytoken123"
    echo ""
    echo "📁 Available Notebooks:"
    echo "   • src/3d_pcd_segmentation_via_sensor_fusion.ipynb (Full original notebook)"
    echo "   • src/demo_notebook.ipynb (Simplified demo version)"
    echo ""
    echo "🔧 Container Management:"
    echo "   • View logs: docker logs pcd-jupyter"
    echo "   • Stop: docker stop pcd-jupyter"
    echo "   • Remove: docker rm pcd-jupyter"
    echo "   • Restart: docker restart pcd-jupyter"
    echo ""
    echo "📚 Documentation: See CLAUDE.md for complete setup guide"
else
    echo "❌ Container failed to start. Check logs with: docker logs pcd-jupyter"
    exit 1
fi
