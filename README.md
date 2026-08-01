# x-maqina: Supreme AI Framework for Multi-Tasking Operations

[![GEMINI XPRIZE](https://img.shields.io/badge/Build%20with-Gemini%20XPRIZE-blue)](https://buildwithgemini.dev/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Vision

x-maqina bridges the gap between advanced AI capabilities and lightning-fast execution for complex state tasks. Powered by **Google's Gemini API**, it delivers autonomous problem-solving, deep system logic, and real-time decision-making across multiple operational domains.

## Core Capabilities

- **🔐 Cybersecurity Operations** — Threat detection, vulnerability assessment, security orchestration
- **💰 Financial/Market Analysis** — Real-time market evaluation, risk analysis, trading insights
- **🤖 Autonomous Decision-Making** — Context-aware decisions with multi-agent reasoning
- **🔧 System Diagnostics** — Infrastructure health, performance optimization, anomaly detection
- **🧠 Multi-Agent Reasoning** — Collaborative AI agents for complex problem decomposition
- **⚡ Low-Latency Processing** — Microsecond-level response times via async/gRPC architecture

## Quick Start

### Prerequisites
- Python 3.11+
- Google Cloud account with Gemini API enabled
- Docker (for containerized deployment)

### Installation

```bash
git clone https://github.com/deepConn/x-maqina.git
cd x-maqina
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Running Locally

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Documentation

- [Architecture](docs/architecture.md)
- [Gemini API Integration](docs/gemini_integration.md)
- [API Reference](docs/api.md)

## License

MIT License - See [LICENSE](LICENSE) for details
