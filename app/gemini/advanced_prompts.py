"""Advanced prompt engineering for domain-specific tasks"""

from typing import Dict, Any, Optional


class PromptEngineer:
    """Advanced prompt engineering and optimization"""

    # Cybersecurity threat prompts with chain-of-thought
    THREAT_ANALYSIS_COT = """
You are a cybersecurity expert. Analyze the following threat using chain-of-thought reasoning.

Threat Data: {threat_data}
Context: {context}
Urgency: {urgency}

Provide your analysis in this exact format:
1. Initial Assessment:
   - What is the nature of this threat?
   - What systems could be affected?

2. Risk Evaluation:
   - Severity level (Critical/High/Medium/Low)
   - Impact assessment
   - Likelihood of exploitation

3. Recommendations:
   - Immediate actions
   - Short-term mitigations
   - Long-term solutions

4. Confidence Score: [0-1]
"""

    # Financial market analysis with reasoning
    MARKET_ANALYSIS_COT = """
You are a financial analyst with expertise in technical and fundamental analysis.
Analyze the following market data using structured reasoning.

Market Data: {market_data}
Timeframe: {timeframe}
Analysis Depth: {analysis_depth}

Provide analysis in this format:

1. Data Summary:
   - Current price level
   - Volume analysis
   - Recent price action

2. Technical Analysis:
   - Support/Resistance levels
   - Key indicators
   - Trend analysis

3. Fundamental Factors:
   - Economic indicators
   - Sector dynamics
   - Company/Asset health

4. Recommendation:
   - Trading Signal (BUY/SELL/HOLD)
   - Entry/Exit points
   - Risk/Reward ratio
   - Confidence Score: [0-1]
"""

    # Multi-agent problem solving
    MULTI_AGENT_REASONING = """
You are coordinating {num_agents} specialized AI agents to solve this problem.
Each agent has different expertise and perspective.

Problem: {problem}
Reasoning Depth: {reasoning_depth}

Structure your response as follows:

1. Problem Decomposition:
   - Break down into sub-problems
   - Identify dependencies
   - Assign to agents

2. Agent 1 Analysis (Specialist):
   - Perspective and approach
   - Key findings
   - Recommendations

3. Agent 2 Analysis (Validator):
   - Critical evaluation
   - Risk assessment
   - Alternative approaches

4. Agent 3 Analysis (Executor):
   - Implementation feasibility
   - Resource requirements
   - Timeline

5. Consensus Solution:
   - Integrated recommendation
   - Confidence score
   - Assumptions and limitations
"""

    # Autonomous decision-making with safety
    AUTONOMOUS_DECISION = """
You are an autonomous decision-making system with safety constraints.
Make a decision based on the provided situation and constraints.

Situation: {situation}
Context: {context}
Constraints: {constraints}

Following this exact structure:

1. Situation Analysis:
   - Current state
   - Key variables
   - Uncertainty factors

2. Option Evaluation:
   - List viable options
   - Pros/Cons for each
   - Risk assessment

3. Constraint Verification:
   - Check against all constraints
   - Flag any violations
   - Safety considerations

4. Final Decision:
   - Recommended action
   - Confidence level
   - Rationale
   - Fallback plan if primary fails
"""

    # System diagnostics with root cause analysis
    DIAGNOSTICS_RCA = """
You are a system diagnostics expert performing root cause analysis.
Analyze the system data to identify issues and their root causes.

System Data: {system_data}
Metrics Type: {metrics_type}

Provide analysis in this structure:

1. Symptom Identification:
   - What's wrong?
   - Affected components
   - User impact

2. Baseline Comparison:
   - Normal vs current state
   - Anomalies detected
   - Severity assessment

3. Root Cause Analysis:
   - Most likely causes (ranked)
   - Evidence for each cause
   - Cascading failures

4. Diagnostic Recommendations:
   - Data to collect
   - Monitoring improvements
   - Prevention strategies

5. Remediation Plan:
   - Immediate actions
   - Permanent fixes
   - Testing procedures
"""

    @staticmethod
    def get_threat_analysis_prompt(
        threat_data: str,
        context: str = "general",
        urgency: str = "medium",
        use_cot: bool = True,
    ) -> str:
        """Get threat analysis prompt"""
        if use_cot:
            return PromptEngineer.THREAT_ANALYSIS_COT.format(
                threat_data=threat_data,
                context=context,
                urgency=urgency,
            )
        else:
            return f"Analyze this security threat: {threat_data}\nContext: {context}\nUrgency: {urgency}"

    @staticmethod
    def get_market_analysis_prompt(
        market_data: Dict[str, Any],
        timeframe: str = "1h",
        analysis_depth: str = "standard",
        use_cot: bool = True,
    ) -> str:
        """Get market analysis prompt"""
        market_str = str(market_data)
        if use_cot:
            return PromptEngineer.MARKET_ANALYSIS_COT.format(
                market_data=market_str,
                timeframe=timeframe,
                analysis_depth=analysis_depth,
            )
        else:
            return f"Analyze market: {market_str}\nTimeframe: {timeframe}"

    @staticmethod
    def get_multi_agent_prompt(
        problem: str,
        num_agents: int = 3,
        reasoning_depth: str = "standard",
        use_cot: bool = True,
    ) -> str:
        """Get multi-agent reasoning prompt"""
        if use_cot:
            return PromptEngineer.MULTI_AGENT_REASONING.format(
                problem=problem,
                num_agents=num_agents,
                reasoning_depth=reasoning_depth,
            )
        else:
            return f"Solve this problem with {num_agents} agents: {problem}"

    @staticmethod
    def get_autonomous_decision_prompt(
        situation: str,
        context: Dict[str, Any],
        constraints: list = None,
        use_cot: bool = True,
    ) -> str:
        """Get autonomous decision prompt"""
        if constraints is None:
            constraints = []
        context_str = str(context)
        constraints_str = "\n".join(constraints) if constraints else "None"

        if use_cot:
            return PromptEngineer.AUTONOMOUS_DECISION.format(
                situation=situation,
                context=context_str,
                constraints=constraints_str,
            )
        else:
            return f"Make a decision: {situation}\nContext: {context_str}"

    @staticmethod
    def get_diagnostics_prompt(
        system_data: Dict[str, Any],
        metrics_type: str = "comprehensive",
        use_cot: bool = True,
    ) -> str:
        """Get system diagnostics prompt"""
        system_str = str(system_data)
        if use_cot:
            return PromptEngineer.DIAGNOSTICS_RCA.format(
                system_data=system_str,
                metrics_type=metrics_type,
            )
        else:
            return f"Diagnose system: {system_str}"


# Global prompt engineer instance
prompt_engineer = PromptEngineer()
