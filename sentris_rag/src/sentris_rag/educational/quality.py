"""
Content quality checker for educational materials.
"""

import re
from typing import Any, Dict, List, Optional

import numpy as np
from textblob import TextBlob


class ContentQualityChecker:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize content quality checker."""
        self.config = config or {}
        self.min_quality_score = self.config.get("quality", {}).get(
            "min_quality_score", 0.7
        )
        self.readability_target = self.config.get("quality", {}).get(
            "readability_target", "grade8"
        )

    async def validate_content(
        self, content: Dict[str, Any], content_type: str
    ) -> Dict[str, Any]:
        """
        Validate content quality.

        Args:
            content: Content to validate
            content_type: Type of content (lesson, quiz, etc.)

        Returns:
            Quality report with scores and suggestions
        """
        # Run all quality checks
        check_results = {}

        # Basic content checks
        check_results["structure"] = self._check_structure(content, content_type)
        check_results["completeness"] = self._check_completeness(content, content_type)
        check_results["readability"] = self._check_readability(content)

        # Educational specific checks
        check_results["learning_objectives"] = self._check_learning_objectives(content)
        check_results["engagement"] = self._check_engagement(content)
        check_results["accessibility"] = self._check_accessibility(content)

        # Calculate overall quality score
        quality_score = self._calculate_quality_score(check_results)

        return {
            "quality_score": quality_score,
            "meets_minimum": quality_score >= self.min_quality_score,
            "check_results": check_results,
            "summary": self._generate_summary(check_results, quality_score),
        }

    def _check_structure(
        self, content: Dict[str, Any], content_type: str
    ) -> Dict[str, Any]:
        """Check content structure."""
        score = 1.0
        suggestions = []

        # Check required fields based on content type
        required_fields = self._get_required_fields(content_type)
        missing_fields = [field for field in required_fields if field not in content]

        if missing_fields:
            score -= 0.2 * len(missing_fields)
            suggestions.append(f"Missing required fields: {', '.join(missing_fields)}")

        # Check section organization
        if "sections" in content:
            if not content["sections"]:
                score -= 0.3
                suggestions.append("Content has no sections")
            else:
                # Check section titles
                untitled = sum(
                    1 for section in content["sections"] if not section.get("title")
                )
                if untitled:
                    score -= 0.1 * untitled
                    suggestions.append(f"{untitled} sections are missing titles")

        return {"score": max(0.0, score), "suggestions": suggestions}

    def _check_completeness(
        self, content: Dict[str, Any], content_type: str
    ) -> Dict[str, Any]:
        """Check content completeness."""
        score = 1.0
        suggestions = []

        # Check content length
        total_text = self._extract_text(content)
        word_count = len(total_text.split())

        min_words = self._get_min_words(content_type)
        if word_count < min_words:
            score -= 0.5 * (1 - word_count / min_words)
            suggestions.append(
                f"Content is too short ({word_count} words). "
                f"Aim for at least {min_words} words."
            )

        # Check for empty sections
        if "sections" in content:
            empty_sections = sum(
                1 for section in content["sections"] if not section.get("content")
            )
            if empty_sections:
                score -= 0.2 * empty_sections
                suggestions.append(f"{empty_sections} sections are empty")

        return {"score": max(0.0, score), "suggestions": suggestions}

    def _check_readability(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Check content readability."""
        score = 1.0
        suggestions = []

        text = self._extract_text(content)
        if not text:
            return {"score": 0.0, "suggestions": ["No text content found"]}

        # Calculate readability metrics
        blob = TextBlob(text)
        sentences = blob.sentences

        # Average sentence length
        avg_sentence_length = np.mean([len(str(s).split()) for s in sentences])
        if avg_sentence_length > 25:
            score -= 0.2
            suggestions.append(
                f"Average sentence length ({avg_sentence_length:.1f} words) is too high. "
                "Aim for 15-20 words per sentence."
            )

        # Vocabulary complexity
        complex_words = sum(
            1 for word in blob.words if len(word) > 12 or self._is_complex_word(word)
        )
        complex_ratio = complex_words / len(blob.words)
        if complex_ratio > 0.2:
            score -= 0.2
            suggestions.append(
                f"{complex_ratio:.1%} of words are complex. "
                "Consider using simpler vocabulary."
            )

        return {"score": max(0.0, score), "suggestions": suggestions}

    def _check_learning_objectives(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Check learning objectives quality."""
        score = 1.0
        suggestions = []

        objectives = content.get("learning_objectives", [])
        if not objectives:
            return {"score": 0.0, "suggestions": ["No learning objectives found"]}

        # Check each objective
        for obj in objectives:
            # Check for measurable verbs
            if not any(verb in obj.lower() for verb in self._get_measurable_verbs()):
                score -= 0.2
                suggestions.append(
                    f"Objective '{obj}' lacks measurable verbs. "
                    "Use verbs like 'explain', 'analyze', 'apply'."
                )

            # Check for clarity
            if len(obj.split()) < 3:
                score -= 0.1
                suggestions.append(
                    f"Objective '{obj}' is too brief. " "Provide more specific details."
                )

        return {"score": max(0.0, score), "suggestions": suggestions}

    def _check_engagement(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Check content engagement level."""
        score = 1.0
        suggestions = []

        # Check for interactive elements
        interactive_elements = content.get("interactive_elements", [])
        if not interactive_elements:
            score -= 0.3
            suggestions.append(
                "No interactive elements found. Consider adding quizzes, "
                "exercises, or discussion prompts."
            )

        # Check for multimedia content
        multimedia = content.get("multimedia", [])
        if not multimedia:
            score -= 0.2
            suggestions.append(
                "No multimedia content found. Consider adding images, "
                "videos, or audio elements."
            )

        # Check for real-world examples
        text = self._extract_text(content)
        if not any(
            phrase in text.lower() for phrase in ["for example", "such as", "like"]
        ):
            score -= 0.2
            suggestions.append(
                "Few or no examples found. Include real-world examples "
                "to illustrate concepts."
            )

        return {"score": max(0.0, score), "suggestions": suggestions}

    def _check_accessibility(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Check content accessibility."""
        score = 1.0
        suggestions = []

        # Check for alt text in images
        images = content.get("images", [])
        missing_alt = sum(1 for img in images if not img.get("alt_text"))
        if missing_alt:
            score -= 0.2 * (missing_alt / len(images))
            suggestions.append(f"{missing_alt} images are missing alt text")

        # Check for captions in videos
        videos = content.get("videos", [])
        missing_captions = sum(1 for vid in videos if not vid.get("captions"))
        if missing_captions:
            score -= 0.2 * (missing_captions / len(videos))
            suggestions.append(f"{missing_captions} videos are missing captions")

        # Check for text alternatives
        multimedia = content.get("multimedia", [])
        missing_text_alt = sum(
            1 for item in multimedia if not item.get("text_alternative")
        )
        if missing_text_alt:
            score -= 0.2 * (missing_text_alt / len(multimedia))
            suggestions.append(
                f"{missing_text_alt} multimedia elements are missing "
                "text alternatives"
            )

        return {"score": max(0.0, score), "suggestions": suggestions}

    def _calculate_quality_score(self, check_results: Dict[str, Any]) -> float:
        """Calculate overall quality score."""
        weights = {
            "structure": 0.2,
            "completeness": 0.2,
            "readability": 0.2,
            "learning_objectives": 0.15,
            "engagement": 0.15,
            "accessibility": 0.1,
        }

        weighted_sum = sum(
            check_results[check]["score"] * weights[check] for check in check_results
        )

        return round(weighted_sum, 2)

    def _generate_summary(
        self, check_results: Dict[str, Any], quality_score: float
    ) -> str:
        """Generate quality check summary."""
        summary = [
            f"Overall Quality Score: {quality_score:.2f}",
            f"Minimum Required: {self.min_quality_score}\n",
        ]

        # Add check results
        for check, result in check_results.items():
            summary.append(f"{check.title()}: {result['score']:.2f}")
            if result["suggestions"]:
                summary.extend(f"- {s}" for s in result["suggestions"])
            summary.append("")

        return "\n".join(summary)

    def _extract_text(self, content: Dict[str, Any]) -> str:
        """Extract all text from content."""
        texts = []

        # Add title
        if "title" in content:
            texts.append(content["title"])

        # Add description
        if "description" in content:
            texts.append(content["description"])

        # Add section content
        if "sections" in content:
            for section in content["sections"]:
                if "title" in section:
                    texts.append(section["title"])
                if "content" in section:
                    texts.append(section["content"])

        return " ".join(texts)

    def _is_complex_word(self, word: str) -> bool:
        """Check if a word is complex."""
        # Simple heuristic: words with many syllables
        return len(self._count_syllables(word)) > 3

    def _count_syllables(self, word: str) -> List[str]:
        """Count syllables in a word."""
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        syllables = []
        current = ""

        for i, char in enumerate(word):
            current += char
            if char in vowels:
                if i + 1 < len(word) and word[i + 1] not in vowels:
                    syllables.append(current)
                    current = ""

        if current:
            syllables.append(current)

        return syllables

    def _get_required_fields(self, content_type: str) -> List[str]:
        """Get required fields for content type."""
        base_fields = ["title", "description"]

        type_fields = {
            "lesson": ["learning_objectives", "sections"],
            "quiz": ["questions", "scoring_rubric"],
            "exercise": ["instructions", "solution"],
            "assessment": ["criteria", "rubric"],
        }

        return base_fields + type_fields.get(content_type, [])

    def _get_min_words(self, content_type: str) -> int:
        """Get minimum word count for content type."""
        return {"lesson": 500, "quiz": 200, "exercise": 300, "assessment": 400}.get(
            content_type, 300
        )

    def _get_measurable_verbs(self) -> List[str]:
        """Get list of measurable verbs for learning objectives."""
        return [
            "analyze",
            "apply",
            "calculate",
            "compare",
            "create",
            "define",
            "demonstrate",
            "describe",
            "design",
            "evaluate",
            "explain",
            "identify",
            "illustrate",
            "interpret",
            "organize",
            "plan",
            "predict",
            "solve",
            "summarize",
            "use",
        ]
