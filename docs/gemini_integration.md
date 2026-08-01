# Gemini API Integration Guide

## Setup

1. Create a Google Cloud project
2. Enable Gemini API in Cloud Console
3. Create an API key
4. Set `GEMINI_API_KEY` in `.env`

## REST API Usage

### Basic Request

```python
from app.gemini.client import GeminiClient

client = GeminiClient()
response = await client.generate_content("Analyze this threat...")
```

### Streaming

```python
async for chunk in await client.stream_content(prompt):
    print(chunk)
```

## Models

- `gemini-2.0-flash`: Recommended for fast responses
- `gemini-1.5-pro`: For complex reasoning
- `gemini-1.5-flash`: Balanced performance/cost

## Rate Limiting

Default limits:
- 60 requests/minute per API key
- Monitor usage in Cloud Console

## Cost Optimization

- Cache repeated prompts
- Use streaming for large responses
- Implement request batching
- Monitor token usage
