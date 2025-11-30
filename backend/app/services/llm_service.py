from openai import OpenAI
from typing import List, Dict, Any, Optional
from app.config.settings import settings
import json

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class LLMService:
    """Handles LLM-powered content generation"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

        # Initialize Claude client if API key is available
        self.claude_client = None
        self.claude_model = settings.ANTHROPIC_MODEL
        if ANTHROPIC_AVAILABLE and settings.ANTHROPIC_API_KEY:
            self.claude_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

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

    def _get_job_context(self, job_profile: Dict[str, Any]) -> str:
        """Get job-appropriate context for prompts"""
        role_type = job_profile.get('role_type', 'quantitative professional')
        seniority = job_profile.get('seniority', 'mid')
        teaching_approach = job_profile.get('teaching_approach', 'Balance theory and practice')
        domain_focus = job_profile.get('domain_focus', 'quantitative finance')

        return f"""
Target Role: {role_type} ({seniority} level)
Domain Focus: {domain_focus}
Teaching Approach: {teaching_approach}

IMPORTANT: Frame all explanations for someone preparing to interview for this specific role.
- Use examples relevant to {domain_focus}
- Highlight concepts frequently tested in {role_type} interviews
- Show practical applications in their target domain
"""

    def generate_explanation(
        self,
        topic: str,
        context_chunks: List[str],
        difficulty: int = 3,
        user_context: Optional[str] = None
    ) -> str:
        """Generate a comprehensive educational explanation"""

        difficulty_context = self._get_difficulty_context(difficulty)

        system_prompt = f"""You are an expert educator specializing in quantitative finance, mathematics, and physics.
Create educational content for a learning platform. Your content must be direct, information-dense, and practical.

{difficulty_context}

CRITICAL REQUIREMENTS:
1. NO filler phrases like "Given your expertise..." or "It's clear that..." - start directly with content
2. Use LaTeX for ALL mathematical formulas: inline math with $...$ and display math with $$...$$
3. Include at least one worked example with step-by-step calculations
4. Provide a Python code snippet demonstrating the concept (unless purely theoretical)
5. Focus on real-world quantitative finance applications
6. **INCORPORATE ALL concepts, examples, and theories from the provided context chunks**
7. **If context mentions specific authors, books, or advanced theories (e.g., Bouchaud, heavy-tailed distributions, Lévy distributions, power laws), you MUST include and explain these concepts**

STRUCTURE YOUR RESPONSE AS FOLLOWS:

## Core Concept
[2-3 paragraphs explaining the fundamental idea with appropriate mathematical formulas using LaTeX. MUST integrate concepts from the provided context.]

## Mathematical Formulation
[Key equations with LaTeX. For example: The expectation is defined as $E[X] = \\sum_{{i}} x_{{i}} p(x_{{i}})$ for discrete variables. Include any specialized distributions or formulations mentioned in context.]

## Quantitative Finance Application
[Concrete example showing how this is used in trading, risk management, or portfolio optimization. Draw from context examples.]

## Python Implementation
```python
# Working code example
import numpy as np

# ... implementation ...
```

## Key Takeaways
- [Bullet point 1]
- [Bullet point 2]
- [Bullet point 3]

FORMATTING RULES:
- Use proper markdown headers (##, ###)
- Use LaTeX: $x^2$ for inline, $$\\frac{{a}}{{b}}$$ for display equations
- Use ```python for code blocks
- Use **bold** for key terms
- Be concise but complete (500-800 words total)"""

        context_text = "\n\n".join(context_chunks) if context_chunks else "No additional context available."

        user_prompt = f"""Topic: {topic}

Context from learning materials (YOU MUST INCORPORATE THESE CONCEPTS AND THEORIES):
{context_text}

{f"Additional context: {user_context}" if user_context else ""}

Create educational content following the structure above. Ensure all math uses LaTeX notation and include practical Python code.

IMPORTANT: Draw extensively from the context above. If specific distributions, theories, or authors are mentioned (e.g., heavy-tailed distributions, Lévy distributions, Pareto distributions, power laws, Bouchaud), these MUST appear in your explanation with proper mathematical treatment."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000  # Increased for comprehensive content
        )

        return response.choices[0].message.content

    def generate_explanation_for_job(
        self,
        topic: str,
        context_chunks: List[str],
        job_profile: Dict[str, Any],
        user_context: Optional[str] = None
    ) -> str:
        """Generate educational explanation tailored to specific job target"""

        job_context = self._get_job_context(job_profile)

        system_prompt = f"""You are an expert educator specializing in quantitative finance, mathematics, and physics.
Create educational content for interview preparation. Your content must be direct, information-dense, and practical.

{job_context}

CRITICAL REQUIREMENTS:
1. NO filler phrases like "Given your expertise..." or "It's clear that..." - start directly with content
2. Use LaTeX for ALL mathematical formulas: inline math with $...$ and display math with $$...$$
3. Include at least one worked example with step-by-step calculations
4. Provide a Python code snippet demonstrating the concept (unless purely theoretical)
5. Focus on how this topic appears in {job_profile.get('role_type', 'quantitative finance')} interviews
6. **INCORPORATE ALL concepts, examples, and theories from the provided context chunks**
7. **If context mentions specific authors, books, or advanced theories (e.g., Bouchaud, heavy-tailed distributions, Lévy distributions, power laws), you MUST include and explain these concepts**

STRUCTURE YOUR RESPONSE AS FOLLOWS:

## Core Concept
[2-3 paragraphs explaining the fundamental idea with appropriate mathematical formulas using LaTeX. MUST integrate concepts from the provided context.]

## Mathematical Formulation
[Key equations with LaTeX. For example: The expectation is defined as $E[X] = \\sum_{{i}} x_{{i}} p(x_{{i}})$ for discrete variables. Include any specialized distributions or formulations mentioned in context.]

## Application in {job_profile.get('role_type', 'Quantitative Finance')}
[Concrete example showing how this is used in the target role. Draw from context examples and tailor to {job_profile.get('domain_focus', 'quantitative finance')}.]

## Python Implementation
```python
# Working code example relevant to the role
import numpy as np

# ... implementation ...
```

## Interview Preparation Notes
- Common interview questions about this topic
- Key points interviewers look for
- Pitfalls to avoid

## Key Takeaways
- [Bullet point 1 - role-specific]
- [Bullet point 2 - role-specific]
- [Bullet point 3 - role-specific]

FORMATTING RULES:
- Use proper markdown headers (##, ###)
- Use LaTeX: $x^2$ for inline, $$\\frac{{a}}{{b}}$$ for display equations
- Use ```python for code blocks
- Use **bold** for key terms
- Be concise but complete (500-800 words total)"""

        context_text = "\n\n".join(context_chunks) if context_chunks else "No additional context available."

        user_prompt = f"""Topic: {topic}

Context from learning materials (YOU MUST INCORPORATE THESE CONCEPTS AND THEORIES):
{context_text}

{f"Additional context: {user_context}" if user_context else ""}

Create educational content following the structure above, tailored for someone targeting a {job_profile.get('role_type', 'quantitative finance')} role.

IMPORTANT:
- Draw extensively from the context above
- Frame everything through the lens of interview preparation
- If specific distributions, theories, or authors are mentioned in context, these MUST appear in your explanation"""

        response = self.client.chat.completions.create(
            model=self.model,  # GPT-4 for quality content
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
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

    def generate_rich_section_content(
        self,
        topic_name: str,
        section_title: str,
        section_id: str,
        context_chunks: List[str],
        use_claude: bool = True
    ) -> dict:
        """
        Generate comprehensive, high-quality section content in VALIDATED STRUCTURE

        CRITICAL: Must match the exact structure validated for statistical modeling:
        {
          "introduction": "...",
          "sections": [{"title": "...", "content": "...", "keyFormula": "..."}],
          "keyTakeaways": [...],
          "interviewTips": [...],
          "practiceProblems": [...],
          "resources": [...]
        }

        Uses Claude (Sonnet 3.5) for superior quality
        Falls back to GPT-4 if Claude is unavailable

        Returns:
            Structured dict matching statistical modeling validated format
        """

        context_text = "\n\n---\n\n".join(context_chunks) if context_chunks else "No specific book content available."

        system_prompt = """You are an elite educator specializing in quantitative finance, with deep expertise in mathematics, statistics, and trading.

Your task is to create comprehensive, rigorous learning content for quant interview preparation.

CRITICAL: You MUST return VALID JSON in this EXACT structure (no markdown, no ```json wrapper):

{
  "introduction": "2-3 sentences introducing the concept, its importance in quant interviews, and why mastering it matters. Be direct and substantive.",
  "sections": [
    {
      "title": "Specific concept name (e.g., 'The OLS Problem', 'Deriving the Estimator')",
      "content": "Detailed explanation with LaTeX math. Use $...$ for inline math and $$...$$ for display equations. Include step-by-step derivations, bullet points for clarity, and concrete examples.",
      "keyFormula": "Main formula if applicable (e.g., '\\\\hat{\\\\beta} = (X^TX)^{-1}X^Ty')"
    }
  ],
  "keyTakeaways": [
    "Concise bullet point with key insight, can include LaTeX like $E[X] = \\\\mu$",
    "Another critical point interviewers expect you to know",
    "Third essential concept"
  ],
  "interviewTips": [
    "Practical interview advice (e.g., 'Be ready to derive on whiteboard in <5 min')",
    "Common pitfalls or what interviewers look for",
    "Connection to practical applications"
  ],
  "practiceProblems": [
    {
      "id": 1,
      "difficulty": "Easy",
      "text": "Specific problem with LaTeX if needed"
    },
    {
      "id": 2,
      "difficulty": "Medium",
      "text": "More challenging problem"
    }
  ],
  "resources": [
    {
      "source": "Book name from context",
      "chapter": "Specific chapter/section",
      "pages": "Page numbers if mentioned"
    }
  ]
}

QUALITY STANDARDS (Match validated "Statistical Modeling" example):
- Introduction: Direct, no filler. Immediately state why this matters for interviews
- Sections: 2-4 detailed sections with mathematical rigor
- LaTeX: Use proper notation: $inline$ and $$display$$ (escape backslashes: \\\\)
- Key Formulas: Highlight THE formula to memorize
- Interview Tips: Practical, specific advice
- Practice Problems: 2-3 problems of increasing difficulty
- Resources: Extract from provided book content

CRITICAL:
- Return ONLY valid JSON (no markdown wrapper, no extra text)
- Use \\\\  (double backslash) for LaTeX in JSON strings
- Draw heavily from provided book content
- Be mathematically rigorous but interview-focused"""

        user_prompt = f"""Topic: {topic_name}
Section {section_id}: {section_title}

Book Content to Incorporate:
{context_text}

Generate content matching the EXACT JSON structure specified in the system prompt. This content will be used by candidates preparing for quant interviews at top firms.

Return ONLY the JSON object - no markdown formatting, no ```json wrapper, just the raw JSON."""

        if use_claude and self.claude_client:
            # Use Claude Sonnet 3.5 for superior quality
            try:
                response = self.claude_client.messages.create(
                    model=self.claude_model,
                    max_tokens=4000,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[{
                        "role": "user",
                        "content": user_prompt
                    }]
                )

                content_text = response.content[0].text

                # Parse JSON response
                import json
                try:
                    # Remove markdown wrapper if present
                    if content_text.startswith('```'):
                        # Extract JSON from markdown code block
                        import re
                        json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', content_text, re.DOTALL)
                        if json_match:
                            content_text = json_match.group(1)

                    return json.loads(content_text)
                except json.JSONDecodeError as e:
                    print(f"⚠️  JSON parse error from Claude: {e}")
                    print(f"Raw response: {content_text[:200]}...")
                    # Fall through to GPT-4

            except Exception as e:
                print(f"⚠️  Claude API error: {e}. Falling back to GPT-4.")
                # Fall through to GPT-4

        # Fallback to GPT-4 (or if use_claude=False)
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )

        import json
        return json.loads(response.choices[0].message.content)


# Singleton instance
llm_service = LLMService()
