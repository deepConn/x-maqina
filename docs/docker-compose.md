# Docker Compose Setup Guide for x-maqina

## Overview

This Docker Compose configuration provides a complete local development environment for x-maqina with:

- **FastAPI Application** (Port 8000)
- **gRPC Server** (Port 50051)
- **PostgreSQL Database** (Port 5432)
- **Redis Cache** (Port 6379)
- **Weaviate Vector DB** (Port 8080)
- **Prometheus Monitoring** (Port 9090)
- **Grafana Dashboards** (Port 3000)

## Prerequisites

```bash
# Install Docker & Docker Compose
docker --version  # >= 20.10
docker-compose --version  # >= 1.29
```

## Quick Start

### 1. Set Environment Variables

```bash
# Create .env file
cp .env.example .env

# Edit .env with your values
GEMINI_API_KEY=your_api_key_here
GCP_PROJECT_ID=your_project_id
```

### 2. Start All Services

```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f app
docker-compose logs -f prometheus
docker-compose logs -f grafana
```

### 3. Verify Services

```bash
# Check container status
docker-compose ps

# Test API
curl http://localhost:8000/health

# Test gRPC server
grpcurl -plaintext localhost:50051 list

# Test PostgreSQL
psql -h localhost -U xmaqina -d xmaqina

# Test Redis
redis-cli -h localhost ping

# Test Prometheus
curl http://localhost:9090/api/v1/query?query=up
```

## Service Details

### FastAPI Application
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Metrics**: http://localhost:8000/metrics
- **Health**: http://localhost:8000/health

### gRPC Server
- **Address**: localhost:50051
- **Reflection**: Enabled
- **Proto Services**: 5 (Security, Financial, Diagnostics, Agent, Autonomous)

### PostgreSQL
- **Host**: localhost:5432
- **User**: xmaqina
- **Password**: xmaqina_password
- **Database**: xmaqina

```bash
# Connect to PostgreSQL
psql -h localhost -U xmaqina -d xmaqina
```

### Redis
- **Host**: localhost:6379
- **Database**: 0
- **Persistence**: Enabled (RDB + AOF)

```bash
# Connect to Redis
redis-cli -h localhost
```

### Weaviate Vector Database
- **URL**: http://localhost:8080
- **Schema**: http://localhost:8080/v1/schema
- **Well-known**: http://localhost:8080/v1/.well-known/ready

### Prometheus
- **URL**: http://localhost:9090
- **Config**: `/monitoring/prometheus.yml`
- **Alerts**: `/monitoring/alerts.yml`
- **Data Retention**: 30 days
- **Scrape Interval**: 15s

### Grafana
- **URL**: http://localhost:3000
- **Default User**: admin
- **Default Password**: admin123
- **Dashboards**: Auto-imported from `/monitoring/dashboards/`
- **Data Source**: Prometheus (http://prometheus:9090)

## Accessing Dashboards

1. Open Grafana: http://localhost:3000
2. Login with admin/admin123
3. Dashboards → Browse
4. Select:
   - **x-maqina Overview** — System-wide metrics
   - **x-maqina Gemini API** — API performance
   - **x-maqina Engine Performance** — Domain engines
   - **x-maqina Cache Performance** — Cache metrics

## Common Commands

```bash
# Stop services
docker-compose down

# Restart a service
docker-compose restart app

# View logs with tail
docker-compose logs --tail=50 app

# Scale a service (if applicable)
docker-compose up --scale app=2

# Remove all data (clean slate)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Execute command in container
docker-compose exec app python -c "print('Hello')"

# Open shell in container
docker-compose exec app sh
```

## Database Operations

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U xmaqina -d xmaqina

# Create migration
docker-compose exec app alembic revision --autogenerate -m "migration name"

# Apply migrations
docker-compose exec app alembic upgrade head
```

## Cache Operations

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Clear cache
docker-compose exec redis redis-cli FLUSHDB

# Monitor Redis
docker-compose exec redis redis-cli MONITOR
```

## Monitoring

### View Metrics
```bash
# Prometheus query endpoint
curl 'http://localhost:9090/api/v1/query?query=xmaqina_requests_total'

# Query range
curl 'http://localhost:9090/api/v1/query_range?query=xmaqina_request_duration_seconds&start=2026-08-01T00:00:00Z&end=2026-08-01T12:00:00Z&step=1h'
```

### Alert Management
```bash
# View active alerts
curl http://localhost:9090/api/v1/alerts

# View alert rules
curl http://localhost:9090/api/v1/rules
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Verify connectivity
docker-compose exec app pg_isready -h postgres
```

### Redis Connection Issues
```bash
# Check Redis logs
docker-compose logs redis

# Verify connectivity
docker-compose exec app redis-cli -h redis ping
```

### Prometheus Not Scraping
```bash
# Check targets
curl http://localhost:9090/api/v1/targets

# View scrape failures
docker-compose logs prometheus
```

## Performance Tuning

### Increase PostgreSQL Resources
Edit `docker-compose.yml`:
```yaml
postgres:
  command:
    - "postgres"
    - "-c"
    - "max_connections=200"
    - "-c"
    - "shared_buffers=512MB"
```

### Increase Redis Memory
Edit `docker-compose.yml`:
```yaml
redis:
  command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
```

### Increase Grafana Resources
Add to `grafana` service:
```yaml
deploy:
  resources:
    limits:
      memory: 2G
```

## Cleanup

```bash
# Stop all services
docker-compose down

# Remove volumes (deletes all data)
docker-compose down -v

# Remove images
docker-compose down -v --rmi all
```

## Next Steps

1. **Configure Alerts**: Edit `monitoring/alerts.yml` for your thresholds
2. **Add Integrations**: Connect Slack, PagerDuty, etc. to Alertmanager
3. **Custom Dashboards**: Create additional Grafana dashboards
4. **Load Testing**: Use `locust` or `k6` for performance testing
5. **CI/CD Integration**: Set up GitHub Actions for automated testing

## Support

For issues, check:
- Service logs: `docker-compose logs <service>`
- Health endpoints: `curl http://localhost:8000/health`
- Prometheus targets: http://localhost:9090/targets
