# How to Import Grafana Dashboards

## Prerequisites
- Grafana running and configured with Prometheus datasource
- x-maqina metrics being scraped by Prometheus

## Method 1: Import via Grafana UI

1. Open Grafana: `http://localhost:3000`
2. Go to **Dashboards** → **Import**
3. Paste the JSON content or upload the `.json` file
4. Select **Prometheus** as datasource
5. Click **Import**

## Method 2: Volume Mount (Docker)

Add to `docker-compose.yml`:

```yaml
grafana:
  image: grafana/grafana:latest
  volumes:
    - ./monitoring/dashboards:/etc/grafana/provisioning/dashboards
    - ./monitoring/datasources:/etc/grafana/provisioning/datasources
```

## Method 3: API Import

```bash
curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @monitoring/dashboards/xmaqina-overview.json
```

## Available Dashboards

1. **xmaqina-overview.json** — System-wide overview
   - Request rates and latency
   - System health score
   - Status distribution

2. **xmaqina-gemini.json** — Gemini API monitoring
   - API request rates
   - Latency percentiles
   - Token consumption
   - Success/error rates

3. **xmaqina-engines.json** — Domain engine performance
   - Engine execution rates
   - Execution latency
   - Error distribution

4. **xmaqina-cache.json** — Cache performance
   - Hit rate trends
   - Cache size
   - Hit/miss operations
