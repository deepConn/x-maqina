# gRPC Service Definitions for x-maqina

## Overview

x-maqina provides comprehensive gRPC services for high-performance, low-latency access to all AI operations.

## Services

### SecurityService
Threat analysis, vulnerability scanning, and incident response.

```proto
service SecurityService {
  rpc AnalyzeThreat (ThreatAnalysisRequest) returns (ThreatAnalysisResponse);
  rpc StreamThreatAnalysis (ThreatAnalysisRequest) returns (stream ThreatAnalysisChunk);
  rpc ScanVulnerabilities (VulnerabilityScanRequest) returns (VulnerabilityScanResponse);
  rpc IncidentResponse (IncidentRequest) returns (IncidentResponse);
  rpc GetThreatIntelligence (ThreatIntelligenceRequest) returns (ThreatIntelligenceResponse);
}
```

### FinancialService
Market analysis, portfolio optimization, and risk assessment.

```proto
service FinancialService {
  rpc AnalyzeMarket (MarketAnalysisRequest) returns (MarketAnalysisResponse);
  rpc StreamMarketAnalysis (MarketAnalysisRequest) returns (stream MarketAnalysisChunk);
  rpc OptimizePortfolio (PortfolioRequest) returns (PortfolioOptimizationResponse);
  rpc AssessRisk (RiskAssessmentRequest) returns (RiskAssessmentResponse);
}
```

### DiagnosticsService
System health monitoring, metrics collection, and anomaly detection.

```proto
service DiagnosticsService {
  rpc HealthCheck (HealthCheckRequest) returns (HealthCheckResponse);
  rpc GetPerformanceMetrics (MetricsRequest) returns (PerformanceMetricsResponse);
  rpc DetectAnomalies (AnomalyDetectionRequest) returns (AnomalyDetectionResponse);
  rpc AnalyzeLogs (LogAnalysisRequest) returns (LogAnalysisResponse);
}
```

### AgentService
Multi-agent reasoning and collaboration.

```proto
service AgentService {
  rpc Reason (ReasoningRequest) returns (ReasoningResponse);
  rpc StreamReasoning (ReasoningRequest) returns (stream ReasoningChunk);
  rpc Collaborate (CollaborationRequest) returns (CollaborationResponse);
  rpc GetAgentStatus (AgentStatusRequest) returns (AgentStatusResponse);
}
```

### AutonomousService
Autonomous decision-making and policy execution.

```proto
service AutonomousService {
  rpc MakeDecision (DecisionRequest) returns (DecisionResponse);
  rpc ExecutePolicy (PolicyExecutionRequest) returns (PolicyExecutionResponse);
  rpc GetDecisionHistory (DecisionHistoryRequest) returns (DecisionHistoryResponse);
}
```

## Compilation

```bash
python scripts/compile_protos.py
```

This generates:
- `grpc/gen/xmaqina_pb2.py` — Protocol buffer messages
- `grpc/gen/xmaqina_pb2_grpc.py` — Service stubs

## Running gRPC Server

```bash
python scripts/run_grpc_server.py
```

Server runs on `localhost:50051`

## Client Usage

```python
import grpc
from grpc.gen.xmaqina_pb2_grpc import SecurityServiceStub
from grpc.gen.xmaqina_pb2 import ThreatAnalysisRequest

async with grpc.aio.secure_channel('localhost:50051', grpc.ssl_channel_credentials()) as channel:
    stub = SecurityServiceStub(channel)
    request = ThreatAnalysisRequest(threat_data="...", context="...")
    response = await stub.AnalyzeThreat(request)
```

## Streaming

For real-time data streaming:

```python
async for chunk in stub.StreamThreatAnalysis(request):
    print(chunk.text)
```

## Reflection

Server supports gRPC reflection for dynamic service discovery:

```bash
grpcurl -plaintext localhost:50051 list
```
