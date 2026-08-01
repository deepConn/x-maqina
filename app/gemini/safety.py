"""Safety and content filtering for Gemini API responses"""

import logging
from typing import Dict, List, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class HarmCategory(str, Enum):
    """Gemini harm categories"""
    HARASSMENT = "HARASSMENT"
    HATE_SPEECH = "HATE_SPEECH"
    SEXUALLY_EXPLICIT = "SEXUALLY_EXPLICIT"
    DANGEROUS_CONTENT = "DANGEROUS_CONTENT"


class SafetyRating(str, Enum):
    """Safety probability ratings"""
    NEGLIGIBLE = "NEGLIGIBLE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class SafetyFilter:
    """Safety and content filtering for Gemini responses"""

    # Safety thresholds for blocking
    BLOCK_THRESHOLD = SafetyRating.HIGH

    # Default safety settings for requests
    DEFAULT_SAFETY_SETTINGS = [
        {
            "category": HarmCategory.HARASSMENT.value,
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": HarmCategory.HATE_SPEECH.value,
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": HarmCategory.SEXUALLY_EXPLICIT.value,
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": HarmCategory.DANGEROUS_CONTENT.value,
            "threshold": "BLOCK_LOW_AND_ABOVE",
        },
    ]

    @staticmethod
    def check_safety_ratings(
        safety_ratings: List[Dict[str, Any]],
        allow_medium: bool = False,
    ) -> tuple[bool, List[str]]:
        """Check if content passes safety filters

        Args:
            safety_ratings: List of safety ratings from API
            allow_medium: Whether to allow medium probability issues

        Returns:
            Tuple of (is_safe, issues_found)
        """
        issues = []
        threshold = SafetyRating.MEDIUM if allow_medium else SafetyRating.HIGH

        for rating in safety_ratings:
            category = rating.get("category", "UNKNOWN")
            probability = rating.get("probability", "NEGLIGIBLE")

            # Check if probability exceeds threshold
            if SafetyFilter._compare_ratings(probability, threshold) >= 0:
                issues.append(f"{category}: {probability}")

        is_safe = len(issues) == 0
        return is_safe, issues

    @staticmethod
    def _compare_ratings(rating1: str, rating2: str) -> int:
        """Compare two safety ratings

        Returns:
            Positive if rating1 > rating2
            0 if equal
            Negative if rating1 < rating2
        """
        order = [
            SafetyRating.NEGLIGIBLE,
            SafetyRating.LOW,
            SafetyRating.MEDIUM,
            SafetyRating.HIGH,
            SafetyRating.VERY_HIGH,
        ]

        try:
            r1_idx = order.index(SafetyRating(rating1))
            r2_idx = order.index(SafetyRating(rating2))
            return r1_idx - r2_idx
        except (ValueError, IndexError):
            return 0

    @staticmethod
    def get_safety_settings(
        blocking_mode: str = "medium",
    ) -> List[Dict[str, str]]:
        """Get safety settings for request

        Args:
            blocking_mode: 'low', 'medium', or 'high' blocking level

        Returns:
            List of safety settings for Gemini API
        """
        thresholds = {
            "low": "BLOCK_ONLY_HIGH",
            "medium": "BLOCK_MEDIUM_AND_ABOVE",
            "high": "BLOCK_LOW_AND_ABOVE",
        }

        threshold = thresholds.get(blocking_mode, "BLOCK_MEDIUM_AND_ABOVE")

        return [
            {"category": category.value, "threshold": threshold}
            for category in HarmCategory
        ]

    @staticmethod
    def filter_content(
        content: str,
        max_length: int = 10000,
        strip_urls: bool = False,
    ) -> str:
        """Filter and sanitize content

        Args:
            content: Content to filter
            max_length: Maximum content length
            strip_urls: Whether to remove URLs

        Returns:
            Filtered content
        """
        if not content:
            return content

        # Truncate if too long
        if len(content) > max_length:
            content = content[:max_length] + "...[truncated]"
            logger.warning(f"Content truncated to {max_length} characters")

        # Strip URLs if requested
        if strip_urls:
            import re
            content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)

        return content

    @staticmethod
    def log_safety_issues(
        issues: List[str],
        severity: str = "WARNING",
    ) -> None:
        """Log safety issues

        Args:
            issues: List of safety issues
            severity: Log level (WARNING, ERROR)
        """
        if not issues:
            return

        issue_str = "; ".join(issues)
        if severity.upper() == "ERROR":
            logger.error(f"Safety issues detected: {issue_str}")
        else:
            logger.warning(f"Safety issues detected: {issue_str}")


# Global safety filter instance
safety_filter = SafetyFilter()
