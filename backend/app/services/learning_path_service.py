"""
Learning Path Service - Job-based personalized learning path generation

Responsibilities:
1. Parse job descriptions to extract requirements
2. Check topic coverage in books (Tier 3)
3. Generate optimal learning sequences
4. Provide external resource recommendations for gaps
"""

from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from app.models.database import Node, LearningPath, User
from app.services.llm_service import llm_service
from app.services.vector_store import vector_store
import json
import hashlib
import os

# Configuration: Topic coverage threshold
# For semantic search: 0.9+=identical, 0.7-0.9=very similar, 0.5-0.7=related, <0.5=unrelated
# NOTE: Lowered to 0.45 due to chunking strategy - book chunks often lack explicit topic mentions
# See diagnose_vector_store.py output: "machine learning" in DL book scores 0.48 (chunking issue)
# TODO: Improve chunking to include chapter titles + more context, then raise to 0.55-0.6
TOPIC_COVERAGE_THRESHOLD = float(os.getenv('TOPIC_COVERAGE_THRESHOLD', '0.45'))


# Common role templates for caching
COMMON_ROLE_TEMPLATES = {
    'quant_researcher': {
        'name': 'Quantitative Researcher',
        'typical_requirements': ['statistics', 'machine learning', 'probability theory', 'linear algebra', 'python', 'research methodology'],
        'seniority': 'senior',
        'domain_focus': 'research'
    },
    'quant_trader': {
        'name': 'Quantitative Trader (HFT)',
        'typical_requirements': ['statistics', 'probability', 'market microstructure', 'low latency systems', 'C++', 'python'],
        'seniority': 'mid',
        'domain_focus': 'trading'
    },
    'risk_quant': {
        'name': 'Risk Analyst',
        'typical_requirements': ['statistics', 'probability', 'var models', 'monte carlo', 'risk management', 'python'],
        'seniority': 'mid',
        'domain_focus': 'risk'
    },
    'ml_engineer': {
        'name': 'ML Engineer (Finance)',
        'typical_requirements': ['machine learning', 'deep learning', 'python', 'production systems', 'data engineering'],
        'seniority': 'mid',
        'domain_focus': 'engineering'
    }
}

# External resource recommendations by topic
EXTERNAL_RESOURCES = {
    'c++': [
        {'name': 'LeetCode', 'url': 'https://leetcode.com', 'type': 'practice'},
        {'name': 'CppReference', 'url': 'https://en.cppreference.com', 'type': 'reference'}
    ],
    'data structures': [
        {'name': 'LeetCode', 'url': 'https://leetcode.com/explore/', 'type': 'practice'},
        {'name': 'AlgoExpert', 'url': 'https://www.algoexpert.io', 'type': 'course'}
    ],
    'algorithms': [
        {'name': 'LeetCode', 'url': 'https://leetcode.com/explore/', 'type': 'practice'},
        {'name': 'CLRS (Algorithm textbook)', 'url': 'https://mitpress.mit.edu/9780262046305/', 'type': 'book'}
    ],
    'distributed systems': [
        {'name': 'MIT 6.824', 'url': 'https://pdos.csail.mit.edu/6.824/', 'type': 'course'},
        {'name': 'Designing Data-Intensive Applications', 'url': 'https://dataintensive.net', 'type': 'book'}
    ],
    'system design': [
        {'name': 'System Design Primer', 'url': 'https://github.com/donnemartin/system-design-primer', 'type': 'guide'},
        {'name': 'Grokking System Design', 'url': 'https://www.educative.io/courses/grokking-the-system-design-interview', 'type': 'course'}
    ],
    'default': [
        {'name': 'Google Search', 'url': 'https://google.com', 'type': 'search'},
        {'name': 'Coursera', 'url': 'https://coursera.org', 'type': 'platform'}
    ]
}


class LearningPathService:
    """Generate and manage personalized learning paths based on job requirements"""

    def __init__(self):
        self.llm_service = llm_service
        self.vector_store = vector_store

    def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """
        Use GPT-4o-mini to extract structured information from job posting

        Args:
            job_description: Full job posting text

        Returns:
            {
                'role_type': 'quant_researcher|quant_trader|risk_quant|ml_engineer|other',
                'seniority': 'junior|mid|senior',
                'required_topics': ['topic1', 'topic2', ...],
                'preferred_topics': ['topic1', 'topic2', ...],
                'programming_languages': ['python', 'c++', 'r'],
                'domain_focus': 'options_pricing|market_making|portfolio_optimization|...',
                'firm_type': 'hedge_fund|prop_trading|bank|fintech',
                'teaching_approach': 'Description of how to tailor content'
            }
        """

        system_prompt = """You are an expert in quantitative finance recruiting and job analysis.
Extract structured information from job descriptions with high accuracy."""

        user_prompt = f"""Analyze this quantitative finance job description:

{job_description}

Extract and return ONLY valid JSON (no markdown, no extra text):
{{
    "role_type": "quant_researcher|quant_trader|risk_quant|ml_engineer|other",
    "seniority": "junior|mid|senior",
    "required_topics": ["list of required technical topics/skills"],
    "preferred_topics": ["list of preferred/nice-to-have topics"],
    "implicit_topics": ["topics typically tested but not mentioned: data structures, algorithms, brain teasers, etc."],
    "programming_languages": ["python", "c++", "r", etc.],
    "domain_focus": "brief description of domain focus",
    "firm_type": "hedge_fund|prop_trading|bank|fintech|consulting",
    "teaching_approach": "How to tailor explanations for this role (1-2 sentences)"
}}

Focus on technical topics relevant to learning. Include implicit requirements like:
- Data structures & algorithms (if coding interviews likely)
- Probability brain teasers (if quant researcher)
- Mental math (if trading role)
- System design (if senior engineering role)
"""

        response = self.llm_service.client.chat.completions.create(
            model="gpt-4o-mini",  # Cheap model for parsing
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Low temperature for consistent parsing
            response_format={"type": "json_object"}
        )

        try:
            job_profile = json.loads(response.choices[0].message.content)
            return job_profile
        except json.JSONDecodeError as e:
            print(f"Error parsing job analysis: {e}")
            # Fallback to generic profile
            return {
                "role_type": "other",
                "seniority": "mid",
                "required_topics": [],
                "preferred_topics": [],
                "implicit_topics": [],
                "programming_languages": ["python"],
                "domain_focus": "general quantitative finance",
                "firm_type": "not_specified",
                "teaching_approach": "Balanced approach with theory and practice"
            }

    def check_topic_coverage(self, topic: str, min_score: float = None) -> Dict[str, Any]:
        """
        Tier 3: Check if topic is well-covered in our books

        Args:
            topic: Topic name to check
            min_score: Minimum similarity score to consider covered (default from config)
                      For semantic search: 0.9+=identical, 0.7-0.9=very similar,
                      0.5-0.7=related concepts, <0.5=unrelated

        Returns:
            {
                'covered': bool,
                'topic': str,
                'confidence': float,
                'source': str (if covered),
                'num_chunks': int (if covered),
                'external_resources': list (if not covered)
            }
        """

        # Use configured threshold if not specified
        if min_score is None:
            min_score = TOPIC_COVERAGE_THRESHOLD

        # Search vector store for topic
        try:
            matches = self.vector_store.search(query=topic, top_k=10)
        except Exception as e:
            print(f"⚠️  Error searching for topic '{topic}': {e}")
            matches = []

        # Log search results for debugging
        if matches:
            print(f"  Topic '{topic}': best match score = {matches[0]['score']:.3f} (threshold={min_score})")
        else:
            print(f"  Topic '{topic}': no matches found in vector store")

        if not matches or matches[0]['score'] < min_score:
            # NOT COVERED - provide external resources
            return {
                "covered": False,
                "topic": topic,
                "confidence": matches[0]['score'] if matches else 0.0,
                "external_resources": self._get_external_resources(topic)
            }

        # COVERED - extract source information
        source_book = matches[0]['metadata'].get('source', 'Unknown')
        high_quality_matches = [m for m in matches if m['score'] > min_score]

        return {
            "covered": True,
            "topic": topic,
            "confidence": matches[0]['score'],
            "source": source_book,  # e.g., "ESL", "DL", "Bouchaud"
            "num_chunks": len(high_quality_matches),
            "top_chunk_preview": matches[0]['text'][:200] + "..." if matches else None
        }

    def _get_external_resources(self, topic: str) -> List[Dict[str, str]]:
        """Get external learning resources for topics not in our books"""

        topic_lower = topic.lower()

        # Check for exact matches
        for key in EXTERNAL_RESOURCES:
            if key in topic_lower:
                return EXTERNAL_RESOURCES[key]

        # Default resources
        return EXTERNAL_RESOURCES['default']

    def generate_path_for_job(
        self,
        job_description: str,
        user_id: str,
        db: Session
    ) -> LearningPath:
        """
        Generate complete learning path for a job description

        Steps:
        1. Analyze job description (GPT-4o-mini)
        2. Check coverage for each topic (vector store)
        3. Sequence covered topics into stages (GPT-4o-mini)
        4. Return structured learning path with gaps identified
        """

        # Step 1: Analyze job
        print(f"Analyzing job description for user {user_id}...")
        job_profile = self.analyze_job_description(job_description)

        # Combine required, preferred, and implicit topics
        all_topics = (
            job_profile.get('required_topics', []) +
            job_profile.get('preferred_topics', []) +
            job_profile.get('implicit_topics', [])
        )

        # Remove duplicates while preserving order
        unique_topics = list(dict.fromkeys(all_topics))

        # Step 2: Check coverage for each topic
        print(f"Checking coverage for {len(unique_topics)} topics...")
        coverage_map = {}
        for topic in unique_topics:
            coverage_map[topic] = self.check_topic_coverage(topic)

        covered_topics = [
            {
                "topic": topic,
                "source": info['source'],
                "confidence": info['confidence']
            }
            for topic, info in coverage_map.items()
            if info['covered']
        ]

        uncovered_topics = [
            {
                "topic": topic,
                "confidence": info['confidence'],
                "external_resources": info['external_resources']
            }
            for topic, info in coverage_map.items()
            if not info['covered']
        ]

        coverage_percentage = int((len(covered_topics) / len(unique_topics) * 100)) if unique_topics else 0

        print(f"Coverage: {coverage_percentage}% ({len(covered_topics)}/{len(unique_topics)} topics)")
        if covered_topics:
            print(f"  ✓ Covered topics: {', '.join([t['topic'] for t in covered_topics[:5]])}" +
                  (f" (+{len(covered_topics)-5} more)" if len(covered_topics) > 5 else ""))
        if uncovered_topics:
            print(f"  ✗ Uncovered topics: {', '.join([t['topic'] for t in uncovered_topics[:5]])}" +
                  (f" (+{len(uncovered_topics)-5} more)" if len(uncovered_topics) > 5 else ""))

        # Step 3: Sequence covered topics into learning stages
        if covered_topics:
            stages = self._sequence_topics(
                topics=[t['topic'] for t in covered_topics],
                job_profile=job_profile,
                db=db
            )
        else:
            stages = []

        # Step 4: Create and save learning path
        learning_path = LearningPath(
            user_id=user_id,
            job_description=job_description,
            role_type=job_profile.get('role_type', 'other'),
            stages=stages,
            covered_topics=covered_topics,
            uncovered_topics=uncovered_topics,
            coverage_percentage=coverage_percentage
        )

        db.add(learning_path)
        db.commit()
        db.refresh(learning_path)

        print(f"✓ Learning path generated: {len(stages)} stages, {len(covered_topics)} topics")

        return learning_path

    def _sequence_topics(
        self,
        topics: List[str],
        job_profile: Dict[str, Any],
        db: Session
    ) -> List[Dict[str, Any]]:
        """
        Use LLM to sequence topics into optimal learning stages

        Considers:
        - Prerequisites (fundamentals before advanced)
        - Job interview priority (most tested topics first)
        - Pedagogical flow (logical progression)

        Uses semantic search (vector similarity) to match job topics to database nodes,
        rather than simple string matching, to handle cases like:
        - Job says "machine learning" → matches nodes like "Supervised Learning", "Neural Networks"
        - Job says "statistical modeling" → matches nodes like "Linear Regression", "GLMs"
        """

        # Use semantic search to find nodes related to each topic
        node_id_set = set()  # Track unique node IDs

        print(f"  Matching {len(topics)} topics to database nodes using semantic search...")

        for topic in topics:
            try:
                # Search vector store for content related to this topic
                # Use lower threshold (0.35) than coverage check since we want to find
                # ANY potentially related nodes, not just "covered" topics
                matches = self.vector_store.search(query=topic, top_k=15)

                if matches:
                    # Extract node IDs from chunk metadata
                    for match in matches:
                        if match['score'] >= 0.35:  # Relaxed threshold for matching
                            node_id = match['metadata'].get('node_id')
                            if node_id:
                                node_id_set.add(node_id)

                    best_score = matches[0]['score']
                    print(f"    '{topic}': found {len([m for m in matches if m['score'] >= 0.35])} related nodes (best score: {best_score:.3f})")
                else:
                    print(f"    '{topic}': no matching nodes found in vector store")

            except Exception as e:
                print(f"    ⚠️  Error searching for topic '{topic}': {e}")
                continue

        # Query database to get actual Node objects
        if not node_id_set:
            print("  ⚠️  Warning: No matching nodes found for any topics via semantic search")
            return []

        unique_nodes = db.query(Node).filter(Node.id.in_(node_id_set)).all()
        print(f"  ✓ Matched {len(unique_nodes)} unique nodes for learning path")

        if not unique_nodes:
            print("  ⚠️  Warning: Node IDs from vector store not found in database")
            return []

        # Prepare node info for LLM
        node_info = [
            {
                "id": n.id,
                "title": n.title,
                "category": n.category,
                "difficulty": n.difficulty_level,
                "estimated_time": n.estimated_time_minutes
            }
            for n in unique_nodes
        ]

        system_prompt = """You are an expert curriculum designer for quantitative finance interview preparation.
Create optimal learning sequences that maximize interview readiness."""

        user_prompt = f"""Create a learning path for this role:

Role: {job_profile.get('role_type', 'quantitative researcher')}
Seniority: {job_profile.get('seniority', 'mid')}
Domain Focus: {job_profile.get('domain_focus', 'general')}

Available topics to cover:
{json.dumps(node_info, indent=2)}

Create a structured learning path with 3-5 stages. Return ONLY valid JSON:
{{
    "stages": [
        {{
            "stage_name": "Stage 1: Fundamentals",
            "duration_weeks": 2,
            "description": "Core concepts tested in 90% of interviews",
            "topics": [
                {{"node_id": 1, "title": "...", "priority": "high", "why": "Essential because..."}},
                ...
            ]
        }},
        ...
    ]
}}

Prioritize:
1. Interview-critical topics first (most commonly tested)
2. Prerequisites before dependent topics
3. Practical application over pure theory
4. Balance breadth and depth based on role
"""

        response = self.llm_service.client.chat.completions.create(
            model="gpt-4o-mini",  # Cheap model for sequencing
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,  # Some creativity for good sequencing
            response_format={"type": "json_object"}
        )

        try:
            result = json.loads(response.choices[0].message.content)
            return result.get('stages', [])
        except json.JSONDecodeError as e:
            print(f"Error parsing learning path sequence: {e}")
            # Fallback: simple sequential list
            return [{
                "stage_name": "Learning Path",
                "duration_weeks": len(unique_nodes) // 2,
                "description": "Complete these topics in order",
                "topics": [
                    {"node_id": n.id, "title": n.title, "priority": "medium", "why": "Part of job requirements"}
                    for n in unique_nodes[:10]  # Limit to first 10
                ]
            }]

    def get_next_topic(self, user_id: str, db: Session) -> Optional[Node]:
        """
        Get next recommended topic for user based on their learning path

        Returns:
            Node to study next, or None if no path exists
        """

        # Get user's most recent learning path
        learning_path = db.query(LearningPath).filter(
            LearningPath.user_id == user_id
        ).order_by(LearningPath.created_at.desc()).first()

        if not learning_path or not learning_path.stages:
            return None

        # Get user's completed topics (you'll need to track this in UserProgress)
        # For now, return first topic from first stage
        first_stage = learning_path.stages[0]
        if not first_stage.get('topics'):
            return None

        first_topic = first_stage['topics'][0]
        node_id = first_topic.get('node_id')

        if node_id:
            return db.query(Node).filter(Node.id == node_id).first()

        return None


# Singleton instance
learning_path_service = LearningPathService()
