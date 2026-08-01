# Copilot Feature Plan

Repository: deepConn/x-maqina
Author: deepConn
Created: 2026-08-01

## Purpose

Provide an in-repo "Copilot" assistant that exposes Gemini-powered interactive flows for operators and developers to run threat analyses, market analyses, diagnostics, and multi-agent reasoning. The plan documents design goals, MVP scope, milestones, safety considerations, and implementation notes to integrate Copilot with existing app/gemini components.

## Goals

- Add a lightweight Copilot API and feature surface that reuses existing prompt engineering (app/gemini/advanced_prompts.py) and safety filters (app/gemini/safety.py).
- Support both synchronous and streaming responses from Gemini.
- Ensure responses pass safety checks and are auditable via telemetry and logging.
- Provide clear operator docs and an integration test harness.

## MVP

- features/copilot/plans.md (this file)
- API endpoints: POST /copilot/query (sync), POST /copilot/stream (server-sent events / websocket)
- Prompt wrappers to assemble prompts using PromptEngineer helpers
- Safety gating using SafetyFilter.check_safety_ratings before returning results
- Metrics: hook into existing metrics.track_gemini_call and request/response counters
- Minimal UI example: simple static HTML page demonstrating streaming responses (optional)

## Milestones

1. Design (1 week)
   - Define API contract, input schema, auth requirements, rate limits
   - Define safety policy defaults and telemetry fields
2. Implementation (2 weeks)
   - Implement endpoints under app/api/v1/endpoints/copilot.py
   - Add prompt wrappers in app/gemini/copilot.py that reuse PromptEngineer
   - Wire safety checks and metrics
3. Testing (1 week)
   - Unit tests for prompt generation and safety filtering
   - Integration tests using a mocked Gemini client
4. Documentation & Examples (1 week)
   - Add usage docs in docs/copilot.md and a simple demo UI

## Open questions

- Authentication model: API tokens vs OAuth2 for operator users?
- Streaming protocol preference: server-sent events (SSE) or WebSockets?
- Default safety blocking level for Copilot (low/medium/high)?
- Should Copilot results be persisted (audit logs) by default?

## Security & Privacy

- All Copilot requests must pass SafetyFilter checks; sensitive outputs should be redacted.
- Audit logs must avoid storing secrets or raw PII. Use redaction and hashing for sensitive fields.
- Rate limits and per-user quotas should be enforced to prevent abuse.

## Implementation notes

- Reuse PromptEngineer.get_* helpers in app/gemini/advanced_prompts.py
- Add app/gemini/copilot.py to assemble prompts, manage streaming, and call the Gemini client
- Add endpoints file: app/api/v1/endpoints/copilot.py and include router in app/api/v1/__init__.py
- Use metrics.track_gemini_call decorator for Gemini invocations
- Mock Gemini responses in tests; keep tests deterministic

## Testing

- Unit tests for prompt formatting (tests/gemini/test_copilot_prompts.py)
- Safety filter tests (tests/gemini/test_safety.py)
- Integration test with a local mock server for streaming responses

## Timeline & Ownership

- Owner: @deepConn (repo maintainer)
- Suggested timeline: 4-6 weeks for full feature set; 2-3 weeks for MVP

## Contributors

- core: deepConn
- reviewers: security, infra, docs

