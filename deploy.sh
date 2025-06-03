#!/bin/bash

# Quantum-Secure E-Commerce Deployment Script
# Usage: ./deploy.sh [staging|production]

set -e

ENVIRONMENT=${1:-staging}
DOMAIN="nt209.com"
VPS_USER="root"
VPS_IP="nt209.vps.192.168.10.1"

echo "🚀 Deploying Quantum-Secure E-Commerce to $ENVIRONMENT"

# 1. Build Frontend
echo "📦 Building frontend..."
cd webapp
npm run build
cd ..

# 2. Prepare deployment package
echo "📋 Preparing deployment package..."
rm -rf deploy_package
mkdir -p deploy_package

# Copy necessary files
cp -r crypto deploy_package/
cp -r services deploy_package/
cp -r database deploy_package/
cp -r monitoring deploy_package/
cp -r webapp/dist deploy_package/webapp_dist
cp -r nginx deploy_package/
cp main.py deploy_package/
cp requirements.txt deploy_package/
cp docker-compose.prod.yml deploy_package/
cp Dockerfile deploy_package/
cp .env.example deploy_package/

# Create deployment archive
tar -czf deploy_package.tar.gz deploy_package/

# 3. Upload to VPS
echo "📤 Uploading to VPS..."
scp deploy_package.tar.gz $VPS_USER@$VPS_IP:/opt/

# 4. Deploy on VPS
echo "🔧 Deploying on VPS..."
ssh $VPS_USER@$VPS_IP << 'ENDSSH'
cd /opt
rm -rf quantum-secure-commerce-old
mv quantum-secure-commerce quantum-secure-commerce-old || true
tar -xzf deploy_package.tar.gz
mv deploy_package quantum-secure-commerce
cd quantum-secure-commerce

# Create .env file if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please update .env file with production values!"
fi

# Build and start services
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

echo "✅ Deployment complete!"
ENDSSH

echo "🎉 Deployment finished!"
echo "📌 Next steps:"
echo "1. Update .env file on VPS with production values"
echo "2. Setup SSL certificates with Let's Encrypt"
echo "3. Configure DNS to point to $VPS_IP"
echo "4. Access your site at https://$DOMAIN"