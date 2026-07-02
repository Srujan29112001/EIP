# Quick Start Guide - EIP

Get the Entrepreneurship Intelligence Platform running in 5 minutes!

## Prerequisites

- Docker Desktop installed and running
- Git

## Steps

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd EIP
```

### 2. Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Generate secret keys
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" >> .env
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))" >> .env
```

### 3. Start All Services
```bash
docker-compose up -d
```

This starts:
- PostgreSQL database
- MongoDB
- Redis
- Neo4j
- Kafka
- Backend API
- Frontend dashboard
- Prometheus
- Grafana

### 4. Initialize Database
```bash
# Wait for services to be healthy (30-60 seconds)
docker-compose ps

# Initialize database
docker-compose exec backend python scripts/init_db.py

# Create admin user
docker-compose exec backend python scripts/create_admin.py
```

### 5. Access the Platform

**Frontend Dashboard:**
- URL: http://localhost:8501
- Login: `admin@eip.com`
- Password: `admin123`

**Backend API:**
- URL: http://localhost:8000
- Docs: http://localhost:8000/docs

**Monitoring:**
- Grafana: http://localhost:3001 (admin/admin)
- Prometheus: http://localhost:9090
- Neo4j: http://localhost:7474 (neo4j/neo4j_password)

### 6. Test the System

1. **Login** to the dashboard at http://localhost:8501
2. **Ask a question** in the AI Chat:
   - "What are the tax benefits for startups in India?"
   - "Market size for sustainable fashion?"
   - "How to optimize my business budget?"
3. **Explore** the dashboard and analytics

## Troubleshooting

**Services not starting?**
```bash
# Check logs
docker-compose logs backend

# Restart services
docker-compose restart
```

**Database connection error?**
```bash
# Ensure databases are healthy
docker-compose ps

# Check PostgreSQL
docker-compose exec postgres psql -U eip_user -d eip_db -c "\dt"
```

**Port conflicts?**
```bash
# Change ports in docker-compose.yml
# For example, change 8000:8000 to 8001:8000
```

## Next Steps

1. **Add API Keys** (for real AI responses):
   - Edit `.env`
   - Add `OPENAI_API_KEY=sk-...`
   - Restart: `docker-compose restart backend`

2. **Read Documentation:**
   - `README.md` - Project overview
   - `SETUP.md` - Detailed setup
   - `docs/API.md` - API documentation
   - `docs/ARCHITECTURE.md` - System design

3. **Development:**
   - See `SETUP.md` for local development setup
   - Use `make dev` for development mode

## Common Commands

```bash
# View logs
make logs

# Stop all services
make stop

# Restart all services
make restart

# Clean up everything
make clean

# Run tests
make test
```

## Need Help?

- Check logs: `docker-compose logs -f backend`
- Review documentation in `docs/`
- Open an issue on GitHub

Enjoy building with EIP! 🚀
