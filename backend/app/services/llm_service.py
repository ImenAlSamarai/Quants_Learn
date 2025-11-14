from openai import OpenAI
from typing import List, Dict, Any, Optional
from app.config.settings import settings
import json


class LLMService:
    """Handles LLM-powered content generation"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

        # Define audience profiles for difficulty-aware prompting
        self.difficulty_profiles = {
            1: {
                "audience": "undergraduate student new to quantitative finance",
                "approach": "Use simple language, everyday analogies, minimal equations. Focus on intuition over rigor.",
                "example_level": "Basic numerical examples with step-by-step explanations",
                "math_level": "High school math assumed. Introduce new notation carefully."
            },
            2: {
                "audience": "undergraduate student with foundational mathematical knowledge",
                "approach": "Balance intuition with some formalism. Use analogies alongside equations.",
                "example_level": "Simple real-world finance examples with some calculations",
                "math_level": "Basic calculus and linear algebra. Explain advanced notation."
            },
            3: {
                "audience": "graduate student with strong mathematical background",
                "approach": "Balance intuitive explanations with mathematical rigor. Formal notation is appropriate.",
                "example_level": "Realistic quant finance problems with detailed solutions",
                "math_level": "Calculus, linear algebra, probability assumed. Introduce specialized concepts."
            },
            4: {
                "audience": "PhD student conducting research in quantitative finance",
                "approach": "Focus on subtle points, edge cases, and research implications. Assume comfort with formalism.",
                "example_level": "Research-level examples, cutting-edge applications, implementation details",
                "math_level": "Advanced mathematics assumed. Focus on technical precision."
            },
            5: {
                "audience": "experienced researcher or practitioner",
                "approach": "Technical depth, latest research, computational considerations. Minimal hand-holding.",
                "example_level": "Production-grade implementations, recent papers, advanced techniques",
                "math_level": "Full mathematical rigor. Assume expertise in the field."
            }
        }

    def _get_difficulty_context(self, difficulty: int) -> str:
        """Get audience-appropriate context for prompts"""
        profile = self.difficulty_profiles.get(difficulty, self.difficulty_profiles[3])
        return f"""
Audience: {profile['audience']}
Approach: {profile['approach']}
Examples: {profile['example_level']}
Mathematical Level: {profile['math_level']}
"""

    def generate_explanation(
        self,
        topic: str,
        context_chunks: List[str],
        difficulty: int = 3,
        user_context: Optional[str] = None
    ) -> str:
        """Generate a concise conceptual explanation"""

        difficulty_context = self._get_difficulty_context(difficulty)

        system_prompt = f"""You are an expert educator specializing in quantitative finance, mathematics, and physics.
Your role is to provide clear, concise explanations tailored to your audience's level.

{difficulty_context}

Guidelines:
- Start with the core intuition appropriate for this audience
- Use analogies when helpful (more for beginners, less for experts)
- Connect to practical applications in quant finance
- Be concise but thorough (200-400 words for levels 1-3, 300-500 for levels 4-5)
- Adjust mathematical notation to the audience's level
- Highlight key insights with bullet points"""

        context_text = "\n\n".join(context_chunks) if context_chunks else "No additional context available."

        user_prompt = f"""Topic: {topic}

Context from learning materials:
{context_text}

{f"Additional context: {user_context}" if user_context else ""}

Provide a clear, conceptual explanation of this topic tailored to the audience level specified above.
Focus on building appropriate understanding for this learner."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        return response.choices[0].message.content

    def generate_applied_example(
        self,
        topic: str,
        context_chunks: List[str],
        domain: str = "quant_finance",
        difficulty: int = 3
    ) -> Dict[str, Any]:
        """Generate an applied example in finance/quant research"""

        difficulty_context = self._get_difficulty_context(difficulty)

        system_prompt = f"""You are an expert in quantitative finance and applied mathematics.
Generate practical, real-world examples that demonstrate how concepts are used in:
- Quantitative trading strategies
- Risk management
- Portfolio optimization
- Derivative pricing
- Financial modeling

{difficulty_context}"""

        context_text = "\n\n".join(context_chunks) if context_chunks else ""

        user_prompt = f"""Topic: {topic}
Domain: {domain}

Context:
{context_text}

Generate a concrete, applied example showing how this concept is used in quantitative finance.

Provide your response in the following JSON format:
{{
    "title": "Example title",
    "scenario": "Brief description of the real-world scenario",
    "problem": "The specific problem or question",
    "solution": "Step-by-step solution with explanations",
    "code_snippet": "Python code if applicable (or null)",
    "key_insights": ["insight 1", "insight 2", ...]
}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {
                "title": "Applied Example",
                "scenario": response.choices[0].message.content,
                "problem": "",
                "solution": "",
                "code_snippet": None,
                "key_insights": []
            }

    def generate_quiz(
        self,
        topic: str,
        context_chunks: List[str],
        difficulty: int = 3,
        num_questions: int = 5
    ) -> Dict[str, Any]:
        """Generate an interactive quiz"""

        system_prompt = """You are an expert educator creating assessment questions for quantitative finance students.
Generate thoughtful questions that test understanding, not just memorization."""

        context_text = "\n\n".join(context_chunks) if context_chunks else ""

        user_prompt = f"""Topic: {topic}
Difficulty Level: {difficulty}/5
Number of Questions: {num_questions}

Context:
{context_text}

Generate a quiz with multiple-choice and conceptual questions.

Provide your response in JSON format:
{{
    "questions": [
        {{
            "question": "The question text",
            "type": "multiple_choice" or "conceptual",
            "options": ["A", "B", "C", "D"] (for multiple choice),
            "correct_answer": "The correct option or explanation",
            "explanation": "Why this is correct and others are wrong"
        }}
    ]
}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {"questions": []}

    def generate_visualization_config(
        self,
        topic: str,
        context_chunks: List[str]
    ) -> Dict[str, Any]:
        """Generate configuration for interactive visualization"""

        system_prompt = """You are an expert in data visualization and mathematical education.
Design interactive visualizations that help students explore and understand concepts."""

        context_text = "\n\n".join(context_chunks[:2]) if context_chunks else ""

        user_prompt = f"""Topic: {topic}

Context:
{context_text}

Design an interactive visualization for this concept.

Provide your response in JSON format:
{{
    "visualization_type": "plot_2d|plot_3d|matrix|network|interactive_simulation",
    "title": "Visualization title",
    "description": "What the visualization shows",
    "parameters": {{
        "param_name": {{
            "type": "slider|input|dropdown",
            "min": 0,
            "max": 10,
            "default": 5,
            "label": "Parameter label"
        }}
    }},
    "data_generation": "Description of how to generate data",
    "code_template": "Python/JavaScript code template if applicable"
}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {
                "visualization_type": "plot_2d",
                "title": topic,
                "description": "Interactive visualization",
                "parameters": {},
                "data_generation": "",
                "code_template": None
            }

    def suggest_related_topics(
        self,
        current_topic: str,
        all_topics: List[str],
        user_progress: Optional[List[str]] = None
    ) -> List[str]:
        """Suggest related topics for exploration"""

        system_prompt = """You are an expert curriculum designer for quantitative finance education.
Suggest relevant topics that naturally connect to what the student is currently learning."""

        topics_text = ", ".join(all_topics)
        progress_text = f"Completed topics: {', '.join(user_progress)}" if user_progress else ""

        user_prompt = f"""Current topic: {current_topic}
Available topics: {topics_text}
{progress_text}

Suggest 3-5 related topics the student should explore next. Consider:
- Prerequisites they might need to review
- Natural next steps in the learning progression
- Related applications

Return only a JSON array of topic names: ["topic1", "topic2", ...]"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        try:
            content = response.choices[0].message.content
            # Extract JSON array even if there's additional text
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(content)
        except:
            return []


# Singleton instance
llm_service = LLMService()
