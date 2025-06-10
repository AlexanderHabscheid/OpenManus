"""
Adaptive quiz generation for educational content.
"""

import json
from typing import Any, Dict, List, Optional

from ..rag import RagSystem


class AdaptiveQuizGenerator:
    def __init__(self, rag: RagSystem):
        """Initialize adaptive quiz generator."""
        self.rag = rag

    async def generate_adaptive_quiz(
        self,
        topic: str,
        user_level: float,  # 0.0 to 1.0
        num_questions: int = 10,
        question_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate an adaptive quiz.

        Args:
            topic: Quiz topic
            user_level: User proficiency level (0.0 to 1.0)
            num_questions: Number of questions to generate
            question_types: Optional list of question types to include

        Returns:
            Quiz structure with questions and metadata
        """
        # Set default question types if not provided
        if question_types is None:
            question_types = ["multiple_choice", "true_false", "short_answer"]

        # Get relevant content from knowledge base
        content = await self._gather_content(topic, user_level)

        # Generate questions
        questions = await self._generate_questions(
            content, num_questions, question_types, user_level
        )

        # Structure the quiz
        quiz = {
            "topic": topic,
            "difficulty_level": user_level,
            "questions": questions,
            "adaptive_settings": self._get_adaptive_settings(user_level),
            "scoring_rubric": self._get_scoring_rubric(question_types),
            "metadata": {
                "total_questions": len(questions),
                "question_types": list(set(q["type"] for q in questions)),
                "estimated_duration": len(questions) * 2,  # minutes
            },
        }

        return quiz

    async def _gather_content(
        self, topic: str, user_level: float
    ) -> List[Dict[str, Any]]:
        """Gather relevant content from knowledge base."""
        # Convert user level to difficulty category
        difficulty = self._level_to_difficulty(user_level)

        # Search knowledge base
        results = await self.rag.search(
            query=f"educational content about {topic}",
            filter_criteria={"content_type": "educational", "difficulty": difficulty},
        )

        return results

    def _level_to_difficulty(self, level: float) -> str:
        """Convert numeric level to difficulty category."""
        if level < 0.3:
            return "beginner"
        elif level < 0.6:
            return "intermediate"
        elif level < 0.8:
            return "advanced"
        else:
            return "expert"

    async def _generate_questions(
        self,
        content: List[Dict[str, Any]],
        num_questions: int,
        question_types: List[str],
        user_level: float,
    ) -> List[Dict[str, Any]]:
        """Generate quiz questions from content."""
        questions = []

        for i in range(num_questions):
            # Select question type
            question_type = question_types[i % len(question_types)]

            # Generate question based on type
            if question_type == "multiple_choice":
                question = self._generate_multiple_choice(content, user_level)
            elif question_type == "true_false":
                question = self._generate_true_false(content, user_level)
            else:  # short_answer
                question = self._generate_short_answer(content, user_level)

            questions.append(question)

        return questions

    def _generate_multiple_choice(
        self, content: List[Dict[str, Any]], user_level: float
    ) -> Dict[str, Any]:
        """Generate multiple choice question."""
        # Select content based on difficulty
        content_item = self._select_content_by_difficulty(content, user_level)

        return {
            "type": "multiple_choice",
            "text": f"Based on the content about {content_item['metadata']['topic']}, what is the key concept?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
            "explanation": "Explanation of the correct answer",
            "difficulty": user_level,
            "points": 10,
            "metadata": {
                "concept_tested": content_item["metadata"].get("concept", ""),
                "learning_objective": content_item["metadata"].get("objective", ""),
            },
        }

    def _generate_true_false(
        self, content: List[Dict[str, Any]], user_level: float
    ) -> Dict[str, Any]:
        """Generate true/false question."""
        content_item = self._select_content_by_difficulty(content, user_level)

        return {
            "type": "true_false",
            "text": f"Is the following statement about {content_item['metadata']['topic']} correct?",
            "statement": "Statement to evaluate",
            "correct_answer": True,
            "explanation": "Explanation of why true/false",
            "difficulty": user_level,
            "points": 5,
            "metadata": {
                "concept_tested": content_item["metadata"].get("concept", ""),
                "learning_objective": content_item["metadata"].get("objective", ""),
            },
        }

    def _generate_short_answer(
        self, content: List[Dict[str, Any]], user_level: float
    ) -> Dict[str, Any]:
        """Generate short answer question."""
        content_item = self._select_content_by_difficulty(content, user_level)

        return {
            "type": "short_answer",
            "text": f"Explain the concept of {content_item['metadata']['topic']} in your own words.",
            "sample_answer": "Example of a good answer",
            "keywords": ["keyword1", "keyword2", "keyword3"],
            "rubric": {"understanding": 5, "completeness": 5, "clarity": 5},
            "difficulty": user_level,
            "points": 15,
            "metadata": {
                "concept_tested": content_item["metadata"].get("concept", ""),
                "learning_objective": content_item["metadata"].get("objective", ""),
            },
        }

    def _select_content_by_difficulty(
        self, content: List[Dict[str, Any]], target_difficulty: float
    ) -> Dict[str, Any]:
        """Select content closest to target difficulty."""

        # Convert content difficulties to numeric values
        def difficulty_to_number(diff: str) -> float:
            return {
                "beginner": 0.2,
                "intermediate": 0.5,
                "advanced": 0.7,
                "expert": 0.9,
            }.get(diff, 0.5)

        # Find content closest to target difficulty
        closest_content = min(
            content,
            key=lambda x: abs(
                difficulty_to_number(x["metadata"].get("difficulty", "intermediate"))
                - target_difficulty
            ),
        )

        return closest_content

    def _get_adaptive_settings(self, user_level: float) -> Dict[str, Any]:
        """Get adaptive quiz settings based on user level."""
        return {
            "initial_difficulty": user_level,
            "difficulty_adjustment": {
                "correct_answer": 0.1,  # Increase difficulty
                "wrong_answer": -0.15,  # Decrease difficulty
            },
            "mastery_threshold": 0.8,
            "minimum_questions": 5,
            "maximum_questions": 20,
            "time_limit_minutes": 30,
        }

    def _get_scoring_rubric(self, question_types: List[str]) -> Dict[str, Any]:
        """Get scoring rubric for question types."""
        rubric = {
            "multiple_choice": {"correct": 10, "partial": 0, "wrong": 0},
            "true_false": {"correct": 5, "wrong": 0},
            "short_answer": {
                "excellent": 15,
                "good": 10,
                "fair": 5,
                "poor": 0,
                "criteria": ["understanding", "completeness", "clarity"],
            },
        }

        return {qtype: rubric[qtype] for qtype in question_types if qtype in rubric}
