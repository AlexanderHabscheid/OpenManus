"""
Basic usage examples for the Sentris RAG system.
This file demonstrates core functionality and common use cases.
"""

import asyncio
from pathlib import Path

from sentris_rag import RagSystem, WebSearch
from sentris_rag.educational import (
    AdaptiveQuizGenerator,
    ContentQualityChecker,
    LearningPathGenerator,
)


async def process_document_example():
    """Example of processing a document and generating educational content."""
    # Initialize the RAG system
    rag = RagSystem()

    # Process a PDF document
    doc_path = Path("example_textbook.pdf")
    doc_id = await rag.process_document(doc_path)

    # Generate educational materials
    materials = await rag.generate_materials(doc_id)

    print("Generated Materials:")
    print(f"- Flashcards: {len(materials['flashcards'])}")
    print(f"- Quiz Questions: {len(materials['quiz'])}")
    print(f"- Summary Length: {len(materials['summary'])}")


async def web_search_example():
    """Example of using the web search capabilities."""
    # Initialize web search
    web = WebSearch()

    # Perform a search
    results = await web.search(
        query="quantum computing basics", engine="duckduckgo", num_results=5
    )

    print("\nWeb Search Results:")
    for i, result in enumerate(results["results"], 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Snippet: {result['snippet'][:100]}...")


async def learning_path_example():
    """Example of generating a personalized learning path."""
    # Initialize components
    rag = RagSystem()
    path_gen = LearningPathGenerator(rag)

    # User profile and goals
    user_profile = {
        "level": "intermediate",
        "interests": ["practical applications", "real-world examples"],
        "learning_style": "visual",
    }

    learning_goals = [
        "Understand basic concepts",
        "Apply knowledge to problems",
        "Master advanced topics",
    ]

    # Generate learning path
    path = await path_gen.generate_path(
        user_profile=user_profile,
        course_material="quantum_computing",
        learning_goals=learning_goals,
    )

    print("\nGenerated Learning Path:")
    for i, module in enumerate(path["modules"], 1):
        print(f"Module {i}: {module['title']}")
        print(f"- Difficulty: {module['difficulty']}")
        print(f"- Duration: {module['estimated_duration']} minutes")


async def quiz_generation_example():
    """Example of generating an adaptive quiz."""
    # Initialize components
    rag = RagSystem()
    quiz_gen = AdaptiveQuizGenerator(rag)

    # Generate quiz
    quiz = await quiz_gen.generate_adaptive_quiz(
        topic="quantum computing", user_level=0.7, num_questions=5  # Advanced beginner
    )

    print("\nGenerated Quiz:")
    for i, question in enumerate(quiz["questions"], 1):
        print(f"\nQuestion {i} (Difficulty: {question['difficulty']}):")
        print(question["text"])
        print("Options:")
        for opt in question["options"]:
            print(f"- {opt}")


async def quality_check_example():
    """Example of checking content quality."""
    # Initialize components
    checker = ContentQualityChecker()

    # Example content
    content = {
        "title": "Introduction to Quantum Computing",
        "sections": [
            {
                "title": "Basic Concepts",
                "content": "Quantum computing uses quantum phenomena...",
            }
        ],
    }

    # Check quality
    quality_report = await checker.validate_content(
        content=content, content_type="lesson"
    )

    print("\nContent Quality Report:")
    print(f"Overall Score: {quality_report['quality_score']}")
    print("\nDetailed Results:")
    for check, result in quality_report["check_results"].items():
        print(f"- {check}: {result['score']}")
        if result["suggestions"]:
            print("  Suggestions:")
            for suggestion in result["suggestions"]:
                print(f"  * {suggestion}")


async def main():
    """Run all examples."""
    print("Running Sentris RAG Examples...")

    try:
        # Process document
        await process_document_example()

        # Web search
        await web_search_example()

        # Learning path
        await learning_path_example()

        # Quiz generation
        await quiz_generation_example()

        # Quality check
        await quality_check_example()

    except Exception as e:
        print(f"Error running examples: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
