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

# Curated book recommendations for uncovered topics
# These are highly-regarded books in quantitative finance that should be added to content/
CURATED_BOOK_RECOMMENDATIONS = {
    # Alpha Research & Trading Strategies
    'alpha research': [
        {'title': 'Advances in Financial Machine Learning', 'author': 'Marcos López de Prado', 'year': 2018, 'reason': 'Industry standard for ML-based alpha research'},
        {'title': 'Quantitative Trading', 'author': 'Ernest P. Chan', 'year': 2008, 'reason': 'Practical guide to alpha generation and strategy development'},
        {'title': 'Active Portfolio Management', 'author': 'Grinold & Kahn', 'year': 1999, 'reason': 'Classical text on alpha models and portfolio construction'}
    ],
    'alpha generation': [
        {'title': 'Advances in Financial Machine Learning', 'author': 'Marcos López de Prado', 'year': 2018, 'reason': 'Modern approach to alpha research with ML'},
        {'title': 'Quantitative Equity Portfolio Management', 'author': 'Qian, Hua & Sorensen', 'year': 2007, 'reason': 'Comprehensive coverage of factor models and alpha'}
    ],
    'factor models': [
        {'title': 'Quantitative Equity Portfolio Management', 'author': 'Qian, Hua & Sorensen', 'year': 2007, 'reason': 'Detailed coverage of multi-factor models'},
        {'title': 'Expected Returns', 'author': 'Antti Ilmanen', 'year': 2011, 'reason': 'Deep dive into factor premiums across asset classes'}
    ],

    # Options & Derivatives
    'options pricing': [
        {'title': 'Options, Futures, and Other Derivatives', 'author': 'John C. Hull', 'year': 2017, 'reason': 'Industry bible for derivatives pricing'},
        {'title': 'The Volatility Surface', 'author': 'Jim Gatheral', 'year': 2006, 'reason': 'Advanced treatment of volatility modeling'}
    ],
    'stochastic calculus': [
        {'title': 'Stochastic Calculus for Finance II', 'author': 'Steven Shreve', 'year': 2004, 'reason': 'Rigorous introduction to continuous-time models'},
        {'title': 'Arbitrage Theory in Continuous Time', 'author': 'Tomas Björk', 'year': 2009, 'reason': 'Comprehensive coverage with finance applications'}
    ],
    'volatility modeling': [
        {'title': 'The Volatility Surface', 'author': 'Jim Gatheral', 'year': 2006, 'reason': 'Practitioner guide to vol surface construction'},
        {'title': 'Volatility and Correlation', 'author': 'Riccardo Rebonato', 'year': 2004, 'reason': 'Detailed treatment of correlation and vol dynamics'}
    ],

    # Risk Management
    'risk management': [
        {'title': 'Quantitative Risk Management', 'author': 'McNeil, Frey & Embrechts', 'year': 2015, 'reason': 'Comprehensive QRM textbook'},
        {'title': 'The Concepts and Practice of Mathematical Finance', 'author': 'Mark Joshi', 'year': 2008, 'reason': 'Practical approach to risk and pricing'}
    ],
    'var models': [
        {'title': 'Value at Risk', 'author': 'Philippe Jorion', 'year': 2006, 'reason': 'Standard reference for VaR methodology'},
        {'title': 'Quantitative Risk Management', 'author': 'McNeil, Frey & Embrechts', 'year': 2015, 'reason': 'Modern approach to risk measurement'}
    ],
    'market microstructure': [
        {'title': 'Market Microstructure Theory', 'author': "O'Hara", 'year': 1995, 'reason': 'Classic theoretical foundation'},
        {'title': 'Empirical Market Microstructure', 'author': 'Joel Hasbrouck', 'year': 2007, 'reason': 'Empirical methods for analyzing market data'}
    ],

    # Time Series & Econometrics
    'time series': [
        {'title': 'Time Series Analysis', 'author': 'Hamilton', 'year': 1994, 'reason': 'Comprehensive econometrics textbook'},
        {'title': 'Analysis of Financial Time Series', 'author': 'Ruey S. Tsay', 'year': 2010, 'reason': 'Finance-specific time series methods'}
    ],
    'econometrics': [
        {'title': 'Econometric Analysis', 'author': 'William Greene', 'year': 2017, 'reason': 'Comprehensive econometrics reference'},
        {'title': 'Analysis of Financial Time Series', 'author': 'Ruey S. Tsay', 'year': 2010, 'reason': 'Applied econometrics for finance'}
    ],

    # Portfolio Optimization
    'portfolio optimization': [
        {'title': 'Active Portfolio Management', 'author': 'Grinold & Kahn', 'year': 1999, 'reason': 'Classical optimization framework'},
        {'title': 'Risk and Asset Allocation', 'author': 'Attilio Meucci', 'year': 2005, 'reason': 'Modern approach to portfolio construction'}
    ],
    'mean variance optimization': [
        {'title': 'Portfolio Selection', 'author': 'Harry Markowitz', 'year': 1959, 'reason': 'Original MVO framework (Nobel Prize)'},
        {'title': 'Risk and Asset Allocation', 'author': 'Attilio Meucci', 'year': 2005, 'reason': 'Modern extensions to classical optimization'}
    ],

    # Machine Learning for Finance
    'reinforcement learning': [
        {'title': 'Reinforcement Learning: An Introduction', 'author': 'Sutton & Barto', 'year': 2018, 'reason': 'Foundational RL textbook'},
        {'title': 'Advances in Financial Machine Learning', 'author': 'Marcos López de Prado', 'year': 2018, 'reason': 'RL applications in trading'}
    ],
    'natural language processing': [
        {'title': 'Speech and Language Processing', 'author': 'Jurafsky & Martin', 'year': 2023, 'reason': 'Comprehensive NLP textbook'},
        {'title': 'Machine Learning for Asset Managers', 'author': 'Marcos López de Prado', 'year': 2020, 'reason': 'NLP for financial documents'}
    ],

    # Programming & Implementation
    'high frequency trading': [
        {'title': 'Algorithmic and High-Frequency Trading', 'author': 'Cartea, Jaimungal & Penalva', 'year': 2015, 'reason': 'Mathematical models for HFT'},
        {'title': 'The Science of Algorithmic Trading', 'author': 'Kissell', 'year': 2013, 'reason': 'Implementation and execution'}
    ],
    'backtesting': [
        {'title': 'Advances in Financial Machine Learning', 'author': 'Marcos López de Prado', 'year': 2018, 'reason': 'Modern backtesting methodology avoiding pitfalls'},
        {'title': 'Evidence-Based Technical Analysis', 'author': 'David Aronson', 'year': 2006, 'reason': 'Statistical rigor in backtesting'}
    ],
    'data preprocessing': [
        {'title': 'Advances in Financial Machine Learning', 'author': 'Marcos López de Prado', 'year': 2018, 'reason': 'Financial data-specific preprocessing techniques'},
        {'title': 'Python for Data Analysis', 'author': "Wes McKinney", 'year': 2022, 'reason': 'Practical guide to pandas and data cleaning'}
    ],

    # Fixed Income
    'fixed income': [
        {'title': 'Fixed Income Securities', 'author': 'Tuckman & Serrat', 'year': 2011, 'reason': 'Comprehensive fixed income textbook'},
        {'title': 'Bond Math', 'author': 'Donald J. Smith', 'year': 2011, 'reason': 'Practical bond calculations'}
    ],
    'interest rate models': [
        {'title': 'Interest Rate Models', 'author': 'Damiano Brigo & Fabio Mercurio', 'year': 2006, 'reason': 'Industry standard for IR modeling'},
        {'title': 'Term-Structure Models', 'author': 'Damir Filipović', 'year': 2009, 'reason': 'Mathematical foundations'}
    ],
}

# External resource recommendations by topic (online resources, courses, practice)
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

        NEW: Returns hierarchical topic structure with priority levels

        Args:
            job_description: Full job posting text

        Returns:
            {
                'role_type': 'quant_researcher|quant_trader|risk_quant|ml_engineer|other',
                'seniority': 'junior|mid|senior',
                'firm_type': 'hedge_fund|prop_trading|bank|fintech',
                'domain_focus': 'options_pricing|market_making|...',
                'programming_languages': ['python', 'c++', 'r'],
                'teaching_approach': 'How to tailor content',
                'topic_hierarchy': {
                    'explicit_topics': [
                        {
                            'name': 'topic name',
                            'priority': 'HIGH',
                            'keywords': ['synonym1', 'synonym2'],
                            'mentioned_explicitly': True,
                            'context': 'how it was mentioned in the job'
                        },
                        ...
                    ],
                    'implicit_topics': [
                        {
                            'name': 'topic name',
                            'priority': 'MEDIUM|LOW',
                            'keywords': ['synonym1', 'synonym2'],
                            'reason': 'why this is needed for the role',
                            'mentioned_explicitly': False
                        },
                        ...
                    ]
                }
            }
        """

        system_prompt = """You are an expert in quantitative finance recruiting and job analysis.
Your task is to extract structured, hierarchical topic information from job descriptions.

You must distinguish between:
1. EXPLICIT topics - skills/knowledge directly mentioned in the job description
2. IMPLICIT topics - skills commonly required for this role type, but not explicitly mentioned

For each topic, provide:
- Precise name (e.g., "statistical modeling" not just "statistics")
- Priority level: HIGH (critical for role), MEDIUM (important), LOW (nice-to-have)
- Keywords: related terms, synonyms, or specific techniques
- Context or reason why it's needed"""

        user_prompt = f"""Analyze this quantitative finance job description and extract a hierarchical topic structure:

{job_description}

Return ONLY valid JSON (no markdown, no extra text) with this structure:
{{
    "role_type": "quant_researcher|quant_trader|risk_quant|ml_engineer|data_scientist|other",
    "seniority": "junior|mid|senior",
    "firm_type": "hedge_fund|prop_trading|bank|fintech|consulting|tech",
    "domain_focus": "brief description of primary domain (e.g., 'options pricing', 'market microstructure', 'portfolio optimization')",
    "programming_languages": ["python", "c++", "r", "sql", etc.],
    "teaching_approach": "1-2 sentences on how to tailor explanations for this role",

    "topic_hierarchy": {{
        "explicit_topics": [
            {{
                "name": "precise topic name (e.g., 'time series forecasting', not 'time series')",
                "priority": "HIGH",
                "keywords": ["related terms", "synonyms", "specific techniques"],
                "mentioned_explicitly": true,
                "context": "how/where it was mentioned in the job description"
            }}
        ],
        "implicit_topics": [
            {{
                "name": "topic name",
                "priority": "MEDIUM or LOW",
                "keywords": ["related terms"],
                "mentioned_explicitly": false,
                "reason": "why this is typically required for this role type"
            }}
        ]
    }}
}}

IMPORTANT GUIDELINES:

1. EXPLICIT TOPICS (directly mentioned):
   - Must appear in the job description text
   - Be specific (e.g., "linear regression" not "statistics")
   - Priority is HIGH if in "Requirements", MEDIUM if in "Nice to have"
   - Include context showing where it was mentioned

2. IMPLICIT TOPICS (typical for role, but not mentioned):
   - ONLY add if commonly tested for this role type
   - Examples for quant researcher: probability theory, brain teasers, mental math
   - Examples for engineering roles: data structures, algorithms, system design
   - Priority: MEDIUM if commonly tested, LOW if just helpful background
   - Keep this list SHORT (max 3-5 topics) - be selective!

3. KEYWORDS:
   - Include synonyms, related terms, specific techniques
   - Example: "machine learning" → ["ML", "supervised learning", "model training", "feature engineering"]
   - Example: "time series" → ["ARMA", "ARIMA", "forecasting", "autocorrelation"]

4. AVOID:
   - Generic terms like "statistics" or "mathematics" (be specific!)
   - Over-adding implicit topics (only critical ones)
   - Repeating same concept in both explicit and implicit

Example for a quant researcher role mentioning "statistical modeling, backtesting strategies, Python":

{{
    "topic_hierarchy": {{
        "explicit_topics": [
            {{
                "name": "statistical modeling",
                "priority": "HIGH",
                "keywords": ["regression", "statistical inference", "hypothesis testing", "model fitting"],
                "mentioned_explicitly": true,
                "context": "Listed in core requirements"
            }},
            {{
                "name": "backtesting",
                "priority": "HIGH",
                "keywords": ["strategy testing", "historical simulation", "walk-forward analysis"],
                "mentioned_explicitly": true,
                "context": "Required for validating trading strategies"
            }}
        ],
        "implicit_topics": [
            {{
                "name": "probability theory",
                "priority": "MEDIUM",
                "keywords": ["probability distributions", "expected value", "conditional probability"],
                "mentioned_explicitly": false,
                "reason": "Foundation for statistical modeling; commonly tested in quant researcher interviews"
            }},
            {{
                "name": "brain teasers",
                "priority": "LOW",
                "keywords": ["probability puzzles", "logic problems", "mental math"],
                "mentioned_explicitly": false,
                "reason": "Commonly tested in quant researcher phone screens"
            }}
        ]
    }}
}}
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

            # ============ DEBUG: Print Extracted Job Profile ============
            print("\n" + "="*80)
            print("🤖 GPT-4o-mini JOB ANALYSIS RESULT (Hierarchical Structure)")
            print("="*80)
            print(f"Role Type: {job_profile.get('role_type', 'unknown')}")
            print(f"Seniority: {job_profile.get('seniority', 'unknown')}")
            print(f"Firm Type: {job_profile.get('firm_type', 'unknown')}")
            print(f"Domain Focus: {job_profile.get('domain_focus', 'unknown')}")
            print(f"Programming Languages: {', '.join(job_profile.get('programming_languages', []))}")

            topic_hierarchy = job_profile.get('topic_hierarchy', {})
            explicit_topics = topic_hierarchy.get('explicit_topics', [])
            implicit_topics = topic_hierarchy.get('implicit_topics', [])

            print(f"\n📋 EXPLICIT TOPICS (directly mentioned): {len(explicit_topics)}")
            for i, topic in enumerate(explicit_topics, 1):
                priority_emoji = "🔴" if topic.get('priority') == 'HIGH' else "🟡" if topic.get('priority') == 'MEDIUM' else "🟢"
                print(f"  {i}. {priority_emoji} [{topic.get('priority', 'UNKNOWN')}] {topic.get('name', 'Unknown')}")
                print(f"     Keywords: {', '.join(topic.get('keywords', []))}")
                print(f"     Context: {topic.get('context', 'N/A')}")

            print(f"\n🧠 IMPLICIT TOPICS (typical for role, not mentioned): {len(implicit_topics)}")
            for i, topic in enumerate(implicit_topics, 1):
                priority_emoji = "🔴" if topic.get('priority') == 'HIGH' else "🟡" if topic.get('priority') == 'MEDIUM' else "🟢"
                print(f"  {i}. {priority_emoji} [{topic.get('priority', 'UNKNOWN')}] {topic.get('name', 'Unknown')}")
                print(f"     Keywords: {', '.join(topic.get('keywords', []))}")
                print(f"     Reason: {topic.get('reason', 'N/A')}")

            print(f"\n💡 Teaching Approach: {job_profile.get('teaching_approach', 'N/A')}")
            print("="*80 + "\n")

            return job_profile
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing job analysis: {e}")
            print(f"Response was: {response.choices[0].message.content[:500]}...")
            # Fallback to generic profile with new structure
            return {
                "role_type": "other",
                "seniority": "mid",
                "firm_type": "not_specified",
                "domain_focus": "general quantitative finance",
                "programming_languages": ["python"],
                "teaching_approach": "Balanced approach with theory and practice",
                "topic_hierarchy": {
                    "explicit_topics": [],
                    "implicit_topics": []
                }
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

        # ============ DEBUG: Detailed Match Information ============
        # Group matches by source book
        matches_by_book = {}
        for match in matches:
            source = match.get('metadata', {}).get('source', 'Unknown')
            if source not in matches_by_book:
                matches_by_book[source] = []
            matches_by_book[source].append(match)

        if matches:
            best_match = matches[0]
            print(f"\n  📚 Topic '{topic}': best overall match score = {best_match['score']:.3f} (threshold={min_score})")

            # Show matches grouped by book
            print(f"     └─ Found in {len(matches_by_book)} book(s):")
            for book_name, book_matches in sorted(matches_by_book.items(),
                                                   key=lambda x: x[1][0]['score'],
                                                   reverse=True):
                best_book_match = book_matches[0]
                book_score = best_book_match['score']
                chapter = best_book_match.get('metadata', {}).get('chapter', 'N/A')
                section = best_book_match.get('metadata', {}).get('section', '')
                num_matches = len([m for m in book_matches if m['score'] > min_score])

                # Determine if this book covers the topic (above threshold)
                coverage_status = "✅" if book_score >= min_score else "⚠️"

                print(f"        {coverage_status} {book_name}")
                print(f"           └─ Best score: {book_score:.3f} | Ch.{chapter} | {num_matches} chunks above threshold")

                # Show text preview for books above threshold
                if book_score >= min_score:
                    text_preview = best_book_match.get('text', '')[:100].replace('\n', ' ')
                    print(f"           └─ Preview: \"{text_preview}...\"")
        else:
            print(f"\n  ❌ Topic '{topic}': no matches found in vector store")

        # Determine if topic is covered (ANY book above threshold)
        books_above_threshold = []
        for book_name, book_matches in matches_by_book.items():
            if book_matches[0]['score'] >= min_score:
                books_above_threshold.append({
                    'source': book_name,
                    'confidence': book_matches[0]['score'],
                    'chapter': book_matches[0].get('metadata', {}).get('chapter', 'N/A'),
                    'num_chunks': len([m for m in book_matches if m['score'] >= min_score]),
                    'preview': book_matches[0].get('text', '')[:200] + "..."
                })

        if not books_above_threshold:
            # NOT COVERED - no book meets threshold
            return {
                "covered": False,
                "topic": topic,
                "confidence": matches[0]['score'] if matches else 0.0,
                "external_resources": self._get_external_resources(topic),
                "all_sources": []  # No sources above threshold
            }

        # COVERED - return ALL books that cover this topic
        # Sort by confidence (best book first)
        books_above_threshold.sort(key=lambda x: x['confidence'], reverse=True)

        return {
            "covered": True,
            "topic": topic,
            "confidence": books_above_threshold[0]['confidence'],  # Best overall score
            "source": books_above_threshold[0]['source'],  # Primary source (best match)
            "all_sources": books_above_threshold,  # All books covering this topic
            "num_chunks": sum(b['num_chunks'] for b in books_above_threshold),
            "top_chunk_preview": books_above_threshold[0]['preview']
        }

    def _get_curated_books(self, topic: str) -> List[Dict[str, Any]]:
        """
        Get curated book recommendations for topics not well-covered in our content

        Returns list of highly-regarded quant finance books that should be added to content/
        """
        topic_lower = topic.lower()

        # Try exact match first
        if topic_lower in CURATED_BOOK_RECOMMENDATIONS:
            return CURATED_BOOK_RECOMMENDATIONS[topic_lower]

        # Try partial match (e.g., "alpha" matches "alpha research")
        for key, books in CURATED_BOOK_RECOMMENDATIONS.items():
            if key in topic_lower or topic_lower in key:
                return books

        # No curated books found
        return []

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
        print(f"\n🔍 Step 1: Analyzing job description for user {user_id}...")
        job_profile = self.analyze_job_description(job_description)

        # Extract topics from new hierarchical structure
        topic_hierarchy = job_profile.get('topic_hierarchy', {})
        explicit_topics = topic_hierarchy.get('explicit_topics', [])
        implicit_topics = topic_hierarchy.get('implicit_topics', [])

        # Create enriched topic list with metadata
        all_topics_enriched = []

        # Add explicit topics (HIGH/MEDIUM priority)
        for topic in explicit_topics:
            all_topics_enriched.append({
                'name': topic.get('name', ''),
                'priority': topic.get('priority', 'MEDIUM'),
                'keywords': topic.get('keywords', []),
                'mentioned_explicitly': True,
                'context': topic.get('context', ''),
                'tier': 'EXPLICIT'
            })

        # Add implicit topics (MEDIUM/LOW priority)
        for topic in implicit_topics:
            all_topics_enriched.append({
                'name': topic.get('name', ''),
                'priority': topic.get('priority', 'LOW'),
                'keywords': topic.get('keywords', []),
                'mentioned_explicitly': False,
                'reason': topic.get('reason', ''),
                'tier': 'IMPLICIT'
            })

        # ============ DEBUG: Show Topic Breakdown ============
        print("\n" + "="*80)
        print("📝 TOPIC EXTRACTION SUMMARY (Hierarchical)")
        print("="*80)
        print(f"Total Topics to Check: {len(all_topics_enriched)}")
        print(f"  • Explicit (directly mentioned): {len(explicit_topics)}")
        print(f"  • Implicit (typical for role): {len(implicit_topics)}")

        print("\n🎯 Topics by Priority:")
        high_priority = [t for t in all_topics_enriched if t['priority'] == 'HIGH']
        medium_priority = [t for t in all_topics_enriched if t['priority'] == 'MEDIUM']
        low_priority = [t for t in all_topics_enriched if t['priority'] == 'LOW']

        print(f"  • HIGH priority: {len(high_priority)}")
        print(f"  • MEDIUM priority: {len(medium_priority)}")
        print(f"  • LOW priority: {len(low_priority)}")

        print("\n📋 All Topics (ordered by priority):")
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        sorted_topics = sorted(all_topics_enriched, key=lambda x: priority_order.get(x['priority'], 3))

        for i, topic in enumerate(sorted_topics, 1):
            priority_emoji = "🔴" if topic['priority'] == 'HIGH' else "🟡" if topic['priority'] == 'MEDIUM' else "🟢"
            tier_label = "EXPLICIT" if topic['mentioned_explicitly'] else "IMPLICIT"
            print(f"  {i}. {priority_emoji} [{topic['priority']}] [{tier_label}] {topic['name']}")
        print("="*80 + "\n")

        # Step 2: Check coverage for each topic (with enriched metadata)
        print(f"🔍 Step 2: Checking coverage for {len(all_topics_enriched)} topics against our book database...")
        print("="*80)
        coverage_map = {}
        for topic_info in all_topics_enriched:
            topic_name = topic_info['name']
            # Search using both topic name and keywords for better matching
            coverage_map[topic_name] = {
                'coverage': self.check_topic_coverage(topic_name),
                'metadata': topic_info  # Preserve priority, keywords, tier, etc.
            }

        # Build covered topics with enriched metadata
        covered_topics = []
        for topic_name, data in coverage_map.items():
            coverage = data['coverage']
            metadata = data['metadata']

            if coverage['covered']:
                covered_topics.append({
                    "topic": topic_name,
                    "source": coverage['source'],  # Primary source (best match)
                    "all_sources": coverage.get('all_sources', []),  # All books covering this topic
                    "confidence": coverage['confidence'],
                    # NEW: Include enriched metadata
                    "priority": metadata.get('priority', 'MEDIUM'),
                    "tier": metadata.get('tier', 'EXPLICIT'),
                    "keywords": metadata.get('keywords', []),
                    "mentioned_explicitly": metadata.get('mentioned_explicitly', True)
                })

        # Build uncovered topics with enriched metadata
        uncovered_topics = []
        for topic_name, data in coverage_map.items():
            coverage = data['coverage']
            metadata = data['metadata']

            if not coverage['covered']:
                uncovered_topics.append({
                    "topic": topic_name,
                    "confidence": coverage['confidence'],
                    "external_resources": coverage['external_resources'],
                    # NEW: Include enriched metadata
                    "priority": metadata.get('priority', 'MEDIUM'),
                    "tier": metadata.get('tier', 'EXPLICIT'),
                    "keywords": metadata.get('keywords', []),
                    "mentioned_explicitly": metadata.get('mentioned_explicitly', True)
                })

        total_topics = len(all_topics_enriched)
        coverage_percentage = int((len(covered_topics) / total_topics * 100)) if total_topics else 0

        # ============ DEBUG: Final Coverage Summary (with enriched metadata) ============
        print("\n" + "="*80)
        print("📊 COVERAGE ANALYSIS COMPLETE (Hierarchical)")
        print("="*80)
        print(f"Overall Coverage: {coverage_percentage}% ({len(covered_topics)}/{total_topics} topics)")

        if covered_topics:
            print(f"\n✅ COVERED TOPICS ({len(covered_topics)}):")
            # Sort by priority for better readability
            priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
            covered_sorted = sorted(covered_topics, key=lambda x: priority_order.get(x.get('priority', 'MEDIUM'), 3))

            for i, t in enumerate(covered_sorted, 1):
                priority_emoji = "🔴" if t.get('priority') == 'HIGH' else "🟡" if t.get('priority') == 'MEDIUM' else "🟢"
                tier_label = t.get('tier', 'EXPLICIT')
                print(f"  {i}. {priority_emoji} [{t.get('priority', 'MEDIUM')}] [{tier_label}] {t['topic']}")

                all_sources = t.get('all_sources', [])
                if len(all_sources) > 1:
                    print(f"     └─ Found in {len(all_sources)} books:")
                    for j, source_info in enumerate(all_sources, 1):
                        source_name = source_info['source']
                        conf = source_info['confidence']
                        chapter = source_info.get('chapter', 'N/A')
                        chunks = source_info.get('num_chunks', 0)
                        print(f"        {j}. {source_name} Ch.{chapter} | Score: {conf:.1%} | {chunks} chunks")
                else:
                    # Single source
                    print(f"     └─ Source: {t['source']} | Confidence: {t['confidence']:.1%}")

        if uncovered_topics:
            print(f"\n❌ UNCOVERED TOPICS ({len(uncovered_topics)}):")
            print("   ⚠️  These topics need book content to be added to the platform")
            # Sort by priority for better readability
            priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
            uncovered_sorted = sorted(uncovered_topics, key=lambda x: priority_order.get(x.get('priority', 'MEDIUM'), 3))

            for i, t in enumerate(uncovered_sorted, 1):
                priority_emoji = "🔴" if t.get('priority') == 'HIGH' else "🟡" if t.get('priority') == 'MEDIUM' else "🟢"
                tier_label = t.get('tier', 'EXPLICIT')
                print(f"\n  {i}. {priority_emoji} [{t.get('priority', 'MEDIUM')}] [{tier_label}] {t['topic']}")
                print(f"     └─ Best Score: {t['confidence']:.1%} (below {TOPIC_COVERAGE_THRESHOLD:.1%} threshold)")
                print(f"     └─ Keywords: {', '.join(t.get('keywords', []))}")

                # Get curated book recommendations
                curated_books = self._get_curated_books(t['topic'])

                if curated_books:
                    print(f"\n     📚 RECOMMENDED BOOKS TO ADD (highly-regarded in the field):")
                    for j, book in enumerate(curated_books, 1):
                        print(f"        {j}. '{book['title']}' by {book['author']} ({book['year']})")
                        print(f"           → {book['reason']}")
                    print(f"     💡 ACTION: Add PDF to content/ folder and run indexing script")
                else:
                    print(f"     ⚠️  No curated book recommendations available")
                    print(f"     └─ Online Resources: {len(t['external_resources'])} recommendations")

        print("="*80 + "\n")

        # Step 3: Create staged prerequisite tree with ALL topics (covered + uncovered)
        # Include both so frontend can show full tree with dotted hexagons for uncovered topics
        all_topics_for_tree = covered_topics + uncovered_topics

        if all_topics_for_tree:
            tree_structure = self._sequence_topics(
                topics=all_topics_for_tree,
                job_profile=job_profile,
                db=db
            )
            stages = tree_structure.get('stages', [])
            dependencies = tree_structure.get('dependencies', [])
        else:
            stages = []
            dependencies = []

        # Step 4: Create and save learning path
        learning_path = LearningPath(
            user_id=user_id,
            job_description=job_description,
            role_type=job_profile.get('role_type', 'other'),
            stages=stages,
            dependencies=dependencies,
            covered_topics=covered_topics,
            uncovered_topics=uncovered_topics,
            coverage_percentage=coverage_percentage
        )

        db.add(learning_path)
        db.commit()
        db.refresh(learning_path)

        num_stages = len(stages)
        total_topics = len(all_topics_for_tree)

        print(f"✓ Learning path generated: {num_stages} stages, {total_topics} topics ({len(covered_topics)} covered, {len(uncovered_topics)} uncovered)")
        print(f"✓ Dependencies: {len(dependencies)} prerequisite relationships")

        return learning_path

    def _sequence_topics(
        self,
        topics: List[Dict[str, Any]],  # Now receives enriched topic data
        job_profile: Dict[str, Any],
        db: Session
    ) -> List[Dict[str, Any]]:
        """
        Use LLM to create staged prerequisite tree structure

        Returns:
        - Stages (Foundations → Core Skills → Advanced)
        - Dependencies within each stage
        - Structure suitable for horizontal tree visualization

        Considers:
        - Prerequisites (fundamentals before advanced)
        - Priority levels (HIGH/MEDIUM/LOW)
        - Job interview priority (most tested topics first)
        - Topic coverage status (covered vs uncovered)
        """

        if not topics:
            return []

        # Prepare enriched topic info for GPT
        topic_info = []
        for t in topics:
            topic_info.append({
                "name": t.get('topic', t.get('name', '')),
                "priority": t.get('priority', 'MEDIUM'),
                "tier": t.get('tier', 'EXPLICIT'),
                "covered": t.get('covered', True),  # Whether covered in our books
                "confidence": t.get('confidence', 0.5)
            })

        system_prompt = """You are an expert curriculum designer for quantitative finance interview preparation.
Your task is to create a STAGED PREREQUISITE TREE for optimal learning.

The tree structure should have:
1. Stages (e.g., "Foundations", "Core Skills", "Advanced Applications")
2. Topics within each stage
3. Dependencies showing which topics are prerequisites for others

Format the learning path so that:
- Earlier stages contain prerequisites for later stages
- Within a stage, topics can be learned in parallel (no strict order)
- Dependencies across stages are clear (e.g., "statistics" in Stage 1 → "machine learning" in Stage 2)
"""

        user_prompt = f"""Create a staged prerequisite tree for this role:

Role: {job_profile.get('role_type', 'quantitative researcher')}
Seniority: {job_profile.get('seniority', 'mid')}
Domain Focus: {job_profile.get('domain_focus', 'general')}

Topics to sequence:
{json.dumps(topic_info, indent=2)}

Create a staged learning tree with 2-4 stages. Return ONLY valid JSON:
{{
    "stages": [
        {{
            "stage_number": 1,
            "stage_name": "Foundations",
            "description": "Prerequisites and fundamental concepts",
            "topics": [
                {{
                    "name": "topic name",
                    "priority": "HIGH|MEDIUM|LOW",
                    "prerequisites": [],
                    "why": "Why this topic is in this stage"
                }}
            ]
        }},
        {{
            "stage_number": 2,
            "stage_name": "Core Skills",
            "description": "Building on foundations",
            "topics": [
                {{
                    "name": "topic name",
                    "priority": "HIGH|MEDIUM|LOW",
                    "prerequisites": ["topic from earlier stage"],
                    "why": "Why this topic is in this stage"
                }}
            ]
        }}
    ],
    "dependencies": [
        {{"from": "foundation topic", "to": "dependent topic", "reason": "why needed"}},
        ...
    ]
}}

IMPORTANT GUIDELINES:
1. Stage 1 should have NO prerequisites (foundational topics only)
2. HIGH priority topics should appear in earlier stages
3. Topics with clear prerequisites should be in later stages
4. Keep stages balanced (3-5 topics per stage)
5. Dependencies should cross stage boundaries (not within same stage)
6. Consider pedagogical flow: statistics → machine learning → alpha research

Prioritize:
1. Prerequisites before dependent topics (e.g., probability before statistics)
2. HIGH priority topics in earlier stages
3. Interview-critical topics first
4. Logical learning progression
"""

        response = self.llm_service.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            response_format={"type": "json_object"}
        )

        try:
            result = json.loads(response.choices[0].message.content)

            # Enrich the result with coverage information
            stages = result.get('stages', [])
            dependencies = result.get('dependencies', [])

            # Add coverage info to each topic in the tree
            for stage in stages:
                for topic_node in stage.get('topics', []):
                    topic_name = topic_node['name']

                    # Find matching topic from our coverage data
                    matching_topic = next(
                        (t for t in topics if t.get('topic', t.get('name')) == topic_name),
                        None
                    )

                    if matching_topic:
                        topic_node['covered'] = matching_topic.get('source') is not None
                        topic_node['confidence'] = matching_topic.get('confidence', 0.0)
                        topic_node['tier'] = matching_topic.get('tier', 'EXPLICIT')
                    else:
                        topic_node['covered'] = False
                        topic_node['confidence'] = 0.0

            return {
                'stages': stages,
                'dependencies': dependencies
            }

        except json.JSONDecodeError as e:
            print(f"Error parsing learning path sequence: {e}")
            # Fallback: simple staged structure
            return {
                'stages': [{
                    "stage_number": 1,
                    "stage_name": "Learning Path",
                    "description": "Complete these topics in order",
                    "topics": [
                        {
                            "name": t.get('topic', t.get('name', '')),
                            "priority": t.get('priority', 'MEDIUM'),
                            "prerequisites": [],
                            "why": "Part of job requirements",
                            "covered": t.get('source') is not None,
                            "confidence": t.get('confidence', 0.0)
                        }
                        for t in topics[:10]  # Limit to 10
                    ]
                }],
                'dependencies': []
            }

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
