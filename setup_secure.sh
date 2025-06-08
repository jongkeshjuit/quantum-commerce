#!/bin/bash
# setup_secure.sh

echo "🔐 Setting up Quantum Commerce with Real Security"
echo "================================================"

# 1. Create directories
echo "📁 Creating directories..."
mkdir -p keys/{dilithium,ibe}
mkdir -p logs
mkdir -p secrets
chmod 700 keys secrets

# 2. Generate secrets
echo "🔑 Generating secrets..."
if [ ! -f .env ]; then
    cp .env.example .env
    
    # Generate secure keys
    JWT_SECRET=$(openssl rand -base64 32)
    DILITHIUM_KEY=$(openssl rand -base64 64)
    IBE_KEY=$(openssl rand -base64 32)
    DB_KEY=$(openssl rand -base64 32)
    
    # Update .env file
    sed -i "s/JWT_SECRET_KEY=/JWT_SECRET_KEY=$JWT_SECRET/" .env
    sed -i "s/DILITHIUM_MASTER_KEY=/DILITHIUM_MASTER_KEY=$DILITHIUM_KEY/" .env
    sed -i "s/IBE_MASTER_KEY=/IBE_MASTER_KEY=$IBE_KEY/" .env
    sed -i "s/DATABASE_ENCRYPTION_KEY=/DATABASE_ENCRYPTION_KEY=$DB_KEY/" .env
    
    echo "✅ Secrets generated"
else
    echo "⚠️  .env already exists"
fi

# 3. Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements_crypto.txt

# 4. Start services
echo "🐳 Starting services..."
docker-compose up -d postgres redis

# Wait for services
echo "⏳ Waiting for services..."
sleep 5

# 5. Create database
echo "🗄️ Setting up database..."
python scripts/create_db.py
python scripts/create_tables.py

# 6. Initialize crypto
echo "🔐 Initializing cryptographic systems..."
python -c "
from crypto import DilithiumSigner, IBESystem
print('Initializing Dilithium...')
dilithium = DilithiumSigner()
print('Initializing IBE...')
ibe = IBESystem()
print('✅ Crypto systems initialized')
"

# 7. Run tests
echo "🧪 Running security tests..."
python -m pytest tests/test_security.py -v

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "  python main.py"
echo ""
echo "To run in production:"
echo "  gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker"