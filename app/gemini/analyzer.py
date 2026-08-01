"""Response analysis and quality scoring for Gemini outputs"""

import logging
import re
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ResponseAnalyzer:
    """Analyzes and scores Gemini API responses"""

    @staticmethod
    def score_response_quality(response: str) -> Dict[str, Any]:
        """Score overall response quality

        Args:
            response: Response text to analyze

        Returns:
            Dict with quality metrics
        """
        if not response:
            return {
                "overall_score": 0.0,
                "issues": ["Empty response"],
            }

        metrics = {}

        # Length analysis
        metrics["length_score"] = ResponseAnalyzer._score_length(response)

        # Coherence analysis
        metrics["coherence_score"] = ResponseAnalyzer._score_coherence(response)

        # Structure analysis
        metrics["structure_score"] = ResponseAnalyzer._score_structure(response)

        # Technical accuracy (basic checks)
        metrics["accuracy_score"] = ResponseAnalyzer._score_accuracy(response)

        # Calculate overall score
        overall = sum(metrics.values()) / len(metrics)
        metrics["overall_score"] = overall

        # Identify issues
        metrics["issues"] = ResponseAnalyzer._identify_issues(response, metrics)

        return metrics

    @staticmethod
    def _score_length(response: str) -> float:
        """Score response length appropriateness"""
        length = len(response)
        # Ideal length: 100-2000 characters
        if length < 50:
            return 0.3  # Too short
        elif length < 100:
            return 0.5
        elif length > 2000:
            return 0.8  # Could be verbose
        else:
            return 1.0  # Ideal

    @staticmethod
    def _score_coherence(response: str) -> float:
        """Score response coherence"""
        # Check for common coherence markers
        lines = response.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]

        if not non_empty_lines:
            return 0.0

        # Check for logical flow
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return 0.5

        # Look for transition words
        transitions = [
            'therefore', 'however', 'moreover', 'furthermore',
            'consequently', 'additionally', 'in conclusion'
        ]
        transition_count = sum(
            1 for sent in sentences if any(t in sent.lower() for t in transitions)
        )

        return min(0.5 + (transition_count / len(sentences)), 1.0)

    @staticmethod
    def _score_structure(response: str) -> float:
        """Score response structure quality"""
        score = 0.5

        # Check for numbering/bullets
        if re.search(r'^\d+\.', response, re.MULTILINE):
            score += 0.2
        if re.search(r'^[•\-\*]', response, re.MULTILINE):
            score += 0.15

        # Check for headers/sections
        if re.search(r'^#{1,6}\s', response, re.MULTILINE):
            score += 0.15

        return min(score, 1.0)

    @staticmethod
    def _score_accuracy(response: str) -> float:
        """Basic accuracy scoring (heuristic)"""
        score = 0.7  # Base score

        # Check for common issues
        issues = [
            (r'\b[A-Z]{10,}\b', -0.05),  # Too many caps
            (r'\b(unclear|unknown|unable to)\b', -0.1),  # Uncertainty language
            (r'\$.*?[0-9]+', 0.05),  # Numeric references
        ]

        for pattern, adjustment in issues:
            if re.search(pattern, response, re.IGNORECASE):
                score += adjustment

        return max(min(score, 1.0), 0.0)

    @staticmethod
    def _identify_issues(response: str, metrics: Dict[str, float]) -> List[str]:
        """Identify specific issues in response"""
        issues = []

        if metrics["length_score"] < 0.5:
            issues.append("Response too short for meaningful analysis")

        if metrics["coherence_score"] < 0.5:
            issues.append("Response lacks logical flow")

        if metrics["structure_score"] < 0.5:
            issues.append("Response structure could be improved")

        if metrics["overall_score"] < 0.5:
            issues.append("Overall response quality is below threshold")

        return issues

    @staticmethod
    def extract_confidence(
        response: str,
        default: float = 0.7,
    ) -> float:
        """Extract confidence score from response text"""
        # Look for confidence patterns
        patterns = [
            r'confidence[:\s]+([0-9.]+)',
            r'confidence score[:\s]+([0-9.]+)',
            r'([0-9.]+)\s*(?:confidence|certainty)',
        ]

        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                try:
                    score = float(match.group(1))
                    if 0 <= score <= 1:
                        return score
                except ValueError:
                    continue

        return default

    @staticmethod
    def extract_key_sections(
        response: str,
    ) -> Dict[str, str]:
        """Extract key sections from structured response"""
        sections = {}

        # Look for numbered sections
        pattern = r'^\d+\.\s*([^:]+):?\s*(.+?)(?=^\d+\.|$)'
        matches = re.finditer(pattern, response, re.MULTILINE | re.DOTALL)

        for match in matches:
            title = match.group(1).strip()
            content = match.group(2).strip()
            sections[title] = content

        return sections

    @staticmethod
    def compare_responses(
        response1: str,
        response2: str,
    ) -> Dict[str, Any]:
        """Compare two responses"""
        score1 = ResponseAnalyzer.score_response_quality(response1)
        score2 = ResponseAnalyzer.score_response_quality(response2)

        return {
            "response1_score": score1["overall_score"],
            "response2_score": score2["overall_score"],
            "better_response": 1 if score1["overall_score"] > score2["overall_score"] else 2,
            "score_difference": abs(score1["overall_score"] - score2["overall_score"]),
            "response1_issues": score1["issues"],
            "response2_issues": score2["issues"],
        }


# Global analyzer instance
response_analyzer = ResponseAnalyzer()
