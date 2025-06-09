#!/bin/bash

# Quantum-Secure E-Commerce Setup Script - Fixed Version
set -e

echo "🔐 Quantum-Secure E-Commerce Setup (Fixed)"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $python_version is installed${NC}"

# Install system dependencies first
echo -e "${YELLOW}Installing system dependencies...${NC}"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Check if running on Ubuntu/Debian
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y \
            build-essential \
            python3-dev \
            postgresql-client \
            libpq-dev \
            cmake \
            gcc \
            g++ \
            libssl-dev \
            libffi-dev
        echo -e "${GREEN}✓ System dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠️  Non-Debian system detected. Please install PostgreSQL development files manually.${NC}"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if command -v brew &> /dev/null; then
        brew install postgresql cmake openssl
        echo -e "${GREEN}✓ System dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠️  Homebrew not found. Please install dependencies manually.${NC}"
    fi
fi

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment created${NC}"

# Upgrade pip and install wheel
echo -e "${YELLOW}Upgrading pip and installing wheel...${NC}"
pip install --upgrade pip wheel setuptools
echo -e "${GREEN}✓ Pip upgraded${NC}"

# Try to install psycopg2-binary first
echo -e "${YELLOW}Installing psycopg2-binary...${NC}"
pip install psycopg2-binary==2.9.9 || {
    echo -e "${YELLOW}Failed to install psycopg2-binary, trying alternative...${NC}"
    pip install psycopg[binary]==3.1.12
}
echo -e "${GREEN}✓ PostgreSQL adapter installed${NC}"

# Install other requirements
echo -e "${YELLOW}Installing other requirements...${NC}"
# Create a temporary requirements file without psycopg2-binary
grep -v "psycopg2-binary" requirements.txt > temp_requirements.txt
pip install -r temp_requirements.txt
rm temp_requirements.txt
echo -e "${GREEN}✓ Base requirements installed${NC}"

# Create directory structure
echo -e "${YELLOW}Creating directory structure...${NC}"
mkdir -p {config,crypto,services,models,api,database/migrations,webapp/{public,src/{components,pages,services}},scripts,tests,keys/{ibe,dilithium},logs,nginx/ssl}

# Create necessary Python files to avoid import errors
touch config/__init__.py crypto/__init__.py services/__init__.py models/__init__.py api/__init__.py database/__init__.py

echo -e "${GREEN}✓ Directory structure created${NC}"

# Create .env file if not exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cat > .env << EOL
# Database
DB_USER=qsc_user
DB_PASSWORD=secure_password_change_me
DB_NAME=quantum_commerce
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_PASSWORD=redis_secure_pass_change_me
REDIS_HOST=localhost
REDIS_PORT=6379

# Security
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
JWT_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')

# Crypto
IBE_MASTER_PASSWORD=secure_master_password_change_me
DILITHIUM_KEY_PASSWORD=secure_key_password_change_me

# API
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development

# Frontend
REACT_APP_API_URL=http://localhost:8000
EOL
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠️  Please update the passwords in .env file!${NC}"
fi

# Create the main.py file if it doesn't exist
if [ ! -f main.py ]; then
    echo -e "${YELLOW}Creating main.py...${NC}"
    echo "# Main API file will be created here" > main.py
fi

# Try to install liboqs-python (optional, may fail)
echo -e "${YELLOW}Attempting to install liboqs-python...${NC}"
pip install git+https://github.com/open-quantum-safe/liboqs-python.git 2>/dev/null || {
    echo -e "${YELLOW}⚠️  liboqs-python installation failed. The app will use fallback encryption.${NC}"
    echo -e "${YELLOW}   To use quantum-safe crypto, install liboqs manually later.${NC}"
}

# Create simplified init_crypto.py
cat > scripts/init_crypto.py << 'EOL'
#!/usr/bin/env python3
"""Initialize cryptographic systems - Simplified version"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Crypto initialization will be done when starting the app...")
print("✓ Crypto setup script created")
EOL

chmod +x scripts/init_crypto.py

# Summary
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Setup completed!${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "1. Copy the crypto files to the crypto directory:"
echo -e "   ${GREEN}cp /path/to/ibe_system.py crypto/${NC}"
echo -e "   ${GREEN}cp /path/to/dilithium_signer.py crypto/${NC}"
echo -e ""
echo -e "2. Copy the services files:"
echo -e "   ${GREEN}cp /path/to/payment_service.py services/${NC}"
echo -e ""
echo -e "3. Copy the main.py file:"
echo -e "   ${GREEN}cp /path/to/main.py ./${NC}"
echo -e ""
echo -e "4. Update passwords in ${YELLOW}.env${NC} file"
echo -e ""
echo -e "5. Start PostgreSQL and Redis using Docker:"
echo -e "   ${GREEN}docker-compose up -d postgres redis${NC}"
echo -e ""
echo -e "6. Run the API:"
echo -e "   ${GREEN}source venv/bin/activate${NC}"
echo -e "   ${GREEN}python main.py${NC}"

echo -e "\n${YELLOW}Optional: For full quantum-safe features:${NC}"
echo -e "- Install liboqs: ${GREEN}sudo apt-get install liboqs-dev${NC}"
echo -e "- Then: ${GREEN}pip install git+https://github.com/open-quantum-safe/liboqs-python.git${NC}"