# x-maqina Monitoring & Observability

## Prometheus Metrics

x-maqina exposes comprehensive Prometheus metrics for monitoring and observability.

### Metrics Categories

#### Request Metrics
- `xmaqina_requests_total` — Total HTTP requests (counter)
  - Labels: method, endpoint, status
- `xmaqina_request_duration_seconds` — Request latency (histogram)
  - Labels: method, endpoint

#### Gemini API Metrics
- `xmaqina_gemini_requests_total` — Total Gemini API calls (counter)
  - Labels: model, status
- `xmaqina_gemini_tokens_total` — Token consumption (counter)
  - Labels: model, type (input/output)
- `xmaqina_gemini_latency_seconds` — API latency (histogram)
  - Labels: model
  - Buckets: 0.1, 0.5, 1.0, 2.0, 5.0, 10.0 seconds

#### Cache Metrics
- `xmaqina_cache_hits_total` — Cache hit count (counter)
- `xmaqina_cache_misses_total` — Cache miss count (counter)
- `xmaqina_cache_size_bytes` — Cache size (gauge)

#### Engine Metrics
- `xmaqina_engine_executions_total` — Engine task count (counter)
  - Labels: engine, status
- `xmaqina_engine_duration_seconds` — Execution time (histogram)
  - Labels: engine

#### Agent Metrics
- `xmaqina_agent_tasks_total` — Agent task count (counter)
  - Labels: agent_id, status
- `xmaqina_agent_confidence` — Confidence scores (summary)
  - Labels: agent_id

#### System Health
- `xmaqina_system_health` — Health score 0-1 (gauge)
- `xmaqina_db_connections` — Active DB connections (gauge)
- `xmaqina_redis_connections` — Active Redis connections (gauge)

#### Error Tracking
- `xmaqina_errors_total` — Error count (counter)
  - Labels: error_type, component
- `xmaqina_safety_violations_total` — Safety violations (counter)
  - Labels: category

### Accessing Metrics

```bash
# Prometheus format
curl http://localhost:8000/metrics

# Scrape configuration (prometheus.yml)
scrape_configs:
  - job_name: 'x-maqina'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

## Dashboards

See `monitoring/dashboards/` for Grafana dashboard JSON files.

## Alerting

Example alert rules in `monitoring/alerts.yml`.
