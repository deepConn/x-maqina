"""Gemini prompt templates and engineering"""

# Cybersecurity prompts
THREAT_ANALYSIS_PROMPT = """
Analyze the following security threat and provide:
1. Threat Level (critical/high/medium/low)
2. Detailed Analysis
3. Recommended Actions
4. Confidence Score (0-1)

Threat Data: {threat_data}
Context: {context}
Urgency: {urgency}
"""

# Financial prompts
MARKET_ANALYSIS_PROMPT = """
Analyze the following market data and provide:
1. Market Trend (bullish/bearish/sideways)
2. Trading Signal (buy/sell/hold)
3. Risk Level
4. Price Target
5. Confidence Score

Market Data: {market_data}
Timeframe: {timeframe}
Analysis Depth: {analysis_depth}
"""

# System diagnostics prompts
DIAGNOSTICS_PROMPT = """
Analyze the following system data and identify:
1. Overall Health Status
2. Performance Issues
3. Anomalies Detected
4. Optimization Recommendations

System Data: {system_data}
"""

# Multi-agent reasoning prompts
MULTI_AGENT_PROMPT = """
Break down and solve the following problem using multi-agent reasoning:

Problem: {problem}
Number of Agents: {num_agents}
Reasoning Depth: {reasoning_depth}

Provide:
1. Problem Decomposition
2. Agent Roles and Responsibilities
3. Collaborative Solution
4. Final Recommendation
"""
