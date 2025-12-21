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
# OPTIMIZED: Set to 0.58 after testing with improved chunking (256 tokens, 128 overlap)
# Threshold balances precision (not too many false positives) with recall (catch valid matches)
# Pure semantic search (NO subject filtering) - embeddings handle cross-subject discovery
TOPIC_COVERAGE_THRESHOLD = float(os.getenv('TOPIC_COVERAGE_THRESHOLD', '0.58'))


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

CRITICAL GRANULARITY REQUIREMENT:
Extract PARENT-LEVEL topics suitable for a learning mindmap (5-10 topics total).
Each topic will be expanded into detailed subtopics later, so keep them broad but meaningful.

GRANULARITY LEVELS (Understanding the hierarchy):
Level 1: Job Role → "Machine Learning Researcher" (already known)
Level 2: PARENT TOPICS (what you extract) → "Python programming", "Supervised learning" (5-10 topics)
Level 3: Child topics (generated later) → "NumPy arrays", "Linear regression" (detailed curriculum)
Level 4: Mastery path sections → Week-by-week detailed lessons (auto-generated)

YOUR JOB: Extract Level 2 (PARENT TOPICS) only!

GRANULARITY EXAMPLES:
✅ GOOD Parent Topics (broad, suitable for mindmap):
- "Python programming" (NOT "Python Skills", NOT "NumPy")
- "Supervised learning" (NOT "Machine learning", NOT "Linear regression")
- "Time series analysis" (NOT "Data analysis", NOT "ARIMA models")
- "Risk management" (NOT "Finance", NOT "VaR calculation")
- "Probability theory" (NOT "Math", NOT "Bayes theorem")

❌ BAD - Too vague/generic:
- "Programming skills" → Should be "Python programming" or "R programming"
- "Programming proficiency" → Should be "Python programming" or "R programming"
- "Coding skills" → Should be "Python programming" or "C++ programming"
- "Data science" → Should be "Statistical modeling" or "Machine learning"
- "Math" → Should be "Linear algebra" or "Probability theory"

❌ BAD - Too specific (these are child topics):
- "NumPy arrays" → Too narrow, part of "Python programming"
- "Linear regression" → Too specific, part of "Supervised learning"
- "ARIMA models" → Too specific, part of "Time series analysis"

COMMON MISTAKES TO AVOID - Here are examples of INCORRECT vs CORRECT extractions:

❌ WRONG EXAMPLE 1:
Job mentions: "macro positioning, equity derivatives, retail investor sentiment"
Bad extraction (TOO GENERIC!):
- "Market knowledge"
- "Data handling"
- "Financial analysis"

✅ CORRECT EXAMPLE 1:
Job mentions: "macro positioning, equity derivatives, retail investor sentiment"
Good extraction (USES EXACT TERMS):
- "Macro positioning"
- "Equity derivatives pricing"
- "Retail investor sentiment analysis"

❌ WRONG EXAMPLE 2:
Job mentions: "time series forecasting, ARIMA models, seasonality detection"
Bad extraction (TOO GENERIC!):
- "Statistical analysis"
- "Forecasting skills"
- "Data modeling"

✅ CORRECT EXAMPLE 2:
Job mentions: "time series forecasting, ARIMA models, seasonality detection"
Good extraction (USES EXACT TERMS):
- "Time series forecasting"
- "ARIMA models"
- "Seasonality detection"

❌ WRONG EXAMPLE 3:
Job mentions: "algorithmic trading, market microstructure, order book dynamics"
Bad extraction (TOO GENERIC!):
- "Trading knowledge"
- "Algorithm design"
- "Market understanding"

✅ CORRECT EXAMPLE 3:
Job mentions: "algorithmic trading, market microstructure, order book dynamics"
Good extraction (USES EXACT TERMS):
- "Algorithmic trading"
- "Market microstructure"
- "Order book dynamics"

DETERMINISM REQUIREMENT:
- You MUST extract the SAME topics for the SAME job description EVERY time
- Be 100% consistent and reproducible in your analysis
- Extract topics in a deterministic order (explicit topics first, then implicit)

You must distinguish between:
1. EXPLICIT topics - skills/knowledge directly mentioned in the job description
2. IMPLICIT topics - skills commonly required for this role type, but not explicitly mentioned

For each topic, provide:
- Precise name using EXACT terminology from job description
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

IMPORTANT GUIDELINES FOR PARENT-LEVEL TOPIC EXTRACTION:

1. TARGET COUNT: Extract 5-10 total parent topics (explicit + implicit combined)
   - Not too many (overwhelming mindmap)
   - Not too few (missing coverage)
   - Each parent topic will expand to 3-8 child topics later

2. EXPLICIT TOPICS (directly mentioned in job):
   - Use domain-specific terminology, but at PARENT level
   - If job mentions "NumPy, Pandas, Matplotlib" → extract "Python programming" (parent)
   - If job mentions "linear regression, logistic regression" → extract "Supervised learning" (parent)
   - If job mentions "ARIMA, seasonality, forecasting" → extract "Time series analysis" (parent)
   - Priority is HIGH if in "Requirements", MEDIUM if in "Nice to have"
   - Include context showing where it was mentioned

3. IMPLICIT TOPICS (typical for role, but not mentioned):
   - ONLY add parent-level fundamentals commonly tested
   - Examples for quant researcher: "Probability theory", "Linear algebra" (NOT "Bayes theorem")
   - Examples for engineering roles: "Data structures", "Algorithms" (NOT "Binary trees")
   - Priority: MEDIUM if commonly tested, LOW if just helpful background
   - Keep this list SHORT (max 2-3 implicit topics) - be selective!

4. KEYWORDS (for better RAG matching):
   - Include specific child topics as keywords
   - Example: "Python programming" → ["NumPy", "Pandas", "matplotlib", "data manipulation"]
   - Example: "Supervised learning" → ["linear regression", "logistic regression", "decision trees"]
   - Example: "Time series analysis" → ["ARIMA", "forecasting", "autocorrelation", "seasonality"]
   - These keywords help with coverage checking but are NOT separate topics

5. CONSOLIDATION RULES:
   - If job mentions multiple related specific skills, GROUP into parent topic:
     - "NumPy" + "Pandas" + "matplotlib" → "Python programming"
     - "linear regression" + "logistic regression" → "Supervised learning"
     - "ARIMA" + "forecasting" + "seasonality" → "Time series analysis"
   - Avoid splitting closely related concepts into separate parent topics
   - The detailed breakdown happens in the mastery path, not the mindmap

6. AVOID:
   - Too vague: "Programming skills", "Data science", "Math"
   - Too specific: "NumPy arrays", "Linear regression", "ARIMA models"
   - Inconsistent granularity: mixing broad topics with narrow ones
   - Over-adding topics: keep it 5-10 parent topics total!

EXAMPLE - Job mentioning: "Python, NumPy, pandas, machine learning, linear regression, decision trees, time series, ARIMA"

✅ GOOD Parent-Level Extraction:
{{
    "topic_hierarchy": {{
        "explicit_topics": [
            {{
                "name": "Python programming",
                "priority": "HIGH",
                "keywords": ["NumPy", "pandas", "matplotlib", "data manipulation", "scientific computing"],
                "mentioned_explicitly": true,
                "context": "Required for data analysis and model implementation - Python, NumPy, pandas mentioned"
            }},
            {{
                "name": "Supervised learning",
                "priority": "HIGH",
                "keywords": ["linear regression", "logistic regression", "decision trees", "random forests", "classification"],
                "mentioned_explicitly": true,
                "context": "Core ML requirement - linear regression and decision trees specifically mentioned"
            }},
            {{
                "name": "Time series analysis",
                "priority": "HIGH",
                "keywords": ["ARIMA", "forecasting", "autocorrelation", "seasonality", "stationarity"],
                "mentioned_explicitly": true,
                "context": "Financial forecasting requirement - time series and ARIMA mentioned"
            }}
        ],
        "implicit_topics": [
            {{
                "name": "Probability theory",
                "priority": "MEDIUM",
                "keywords": ["distributions", "expected value", "conditional probability", "Bayes theorem"],
                "mentioned_explicitly": false,
                "reason": "Foundation for ML and statistics; commonly tested in quant interviews"
            }}
        ]
    }}
}}

❌ BAD - Too Specific (these should be consolidated):
{{
    "explicit_topics": [
        {{"name": "NumPy"}},  // Too narrow - part of Python programming
        {{"name": "pandas"}},  // Too narrow - part of Python programming
        {{"name": "linear regression"}},  // Too narrow - part of Supervised learning
        {{"name": "decision trees"}},  // Too narrow - part of Supervised learning
        {{"name": "ARIMA models"}},  // Too narrow - part of Time series analysis
        {{"name": "backtesting",
                "keywords": ["historical simulation", "walk-forward analysis", "strategy validation"],
                "mentioned_explicitly": true,
                "context": "Required for validating trading strategies"
            }}
        ],
        "implicit_topics": [
            {{
                "name": "probability theory",
                "priority": "MEDIUM",
                "keywords": ["probability distributions", "expected value", "stochastic processes"],
                "mentioned_explicitly": false,
                "reason": "Foundation for statistical modeling; commonly tested in quant interviews"
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
            temperature=0.0,  # ZERO temperature for 100% deterministic, reproducible topic extraction
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

    def check_topic_coverage(self, topic: str, min_score: float = None, keywords: list = None) -> Dict[str, Any]:
        """
        Tier 3: Check if topic is well-covered in our books

        Enhanced with keyword fallback: If main topic search yields low scores,
        also searches using keywords to improve matching (zero cost increase).

        Args:
            topic: Topic name to check
            min_score: Minimum similarity score to consider covered (default from config)
                      For semantic search: 0.9+=identical, 0.7-0.9=very similar,
                      0.5-0.7=related concepts, <0.5=unrelated
            keywords: Optional list of related terms/synonyms for fallback search

        Returns:
            {
                'covered': bool,
                'topic': str,
                'confidence': float,
                'source': str (if covered),
                'num_chunks': int (if covered),
                'external_resources': list (if not covered),
                'matched_via': 'topic' or 'keyword' (if keyword fallback used)
            }
        """

        # Use configured threshold if not specified
        if min_score is None:
            min_score = TOPIC_COVERAGE_THRESHOLD

        # Search vector store for topic across ALL namespaces (books + web content)
        # Pure semantic search (NO subject filtering) - embeddings handle cross-subject discovery
        try:
            matches = self.vector_store.search_all_namespaces(
                query=topic,
                top_k=50,  # Increased from 10 for broader semantic coverage
                namespaces=['', 'web_resource']  # Search both book and web content
            )
        except Exception as e:
            print(f"⚠️  Error searching for topic '{topic}': {e}")
            matches = []

        # Check if we should try keyword fallback
        # Use keyword fallback if: 1) keywords provided, 2) main search score is low
        use_keyword_fallback = False
        if keywords and matches:
            best_score = matches[0]['score'] if matches else 0.0
            # If best match is below threshold + margin, try keywords
            if best_score < (min_score + 0.05):
                use_keyword_fallback = True
                print(f"  ℹ️  Topic '{topic}' score ({best_score:.3f}) is borderline. Trying keyword fallback with: {keywords[:3]}")

        # Keyword fallback search
        keyword_matches = []
        if use_keyword_fallback:
            for keyword in keywords[:3]:  # Top 3 keywords only
                try:
                    kw_matches = self.vector_store.search_all_namespaces(
                        query=keyword,
                        top_k=15,  # Increased from 5 for better keyword coverage
                        namespaces=['', 'web_resource']
                    )
                    keyword_matches.extend(kw_matches)
                except Exception as e:
                    print(f"  ⚠️  Error searching keyword '{keyword}': {e}")

            # De-duplicate by chunk text (simple dedup)
            seen_texts = set()
            deduped_keyword_matches = []
            for match in keyword_matches:
                text_snippet = match.get('text', '')[:100]  # First 100 chars as fingerprint
                if text_snippet not in seen_texts:
                    seen_texts.add(text_snippet)
                    deduped_keyword_matches.append(match)

            keyword_matches = deduped_keyword_matches

            if keyword_matches:
                best_keyword_score = max(m['score'] for m in keyword_matches)
                print(f"  ✓ Keyword search found {len(keyword_matches)} additional matches (best: {best_keyword_score:.3f})")

        # Combine main topic matches with keyword matches
        all_matches = matches + keyword_matches
        if all_matches:
            # Sort by score
            all_matches.sort(key=lambda m: m['score'], reverse=True)
            # Remove duplicates again after combining
            seen_texts = set()
            unique_matches = []
            for match in all_matches:
                text_snippet = match.get('text', '')[:100]
                if text_snippet not in seen_texts:
                    seen_texts.add(text_snippet)
                    unique_matches.append(match)
            matches = unique_matches

        # ============ DEBUG: Detailed Match Information ============
        # Group matches by source (books + web resources)
        matches_by_source = {}
        for match in matches:
            source = match.get('metadata', {}).get('source', 'Unknown')
            if source not in matches_by_source:
                matches_by_source[source] = []
            matches_by_source[source].append(match)

        if matches:
            best_match = matches[0]
            print(f"\n  📚 Topic '{topic}': best overall match score = {best_match['score']:.3f} (threshold={min_score})")

            # Show matches grouped by source (books + web)
            print(f"     └─ Found in {len(matches_by_source)} source(s):")
            for source_name, source_matches in sorted(matches_by_source.items(),
                                                       key=lambda x: x[1][0]['score'],
                                                       reverse=True):
                best_source_match = source_matches[0]
                source_score = best_source_match['score']
                num_matches = len([m for m in source_matches if m['score'] > min_score])

                # Determine source type (web or book)
                source_namespace = best_source_match.get('source_namespace', 'default')
                is_web = source_namespace == 'web_resource'

                # Get source-specific metadata
                if is_web:
                    # Web resource metadata
                    url = best_source_match.get('metadata', {}).get('url', 'N/A')
                    topic_name = best_source_match.get('metadata', {}).get('topic', 'N/A')
                    source_icon = "🌐"
                else:
                    # Book metadata
                    chapter = best_source_match.get('metadata', {}).get('chapter', 'N/A')
                    source_icon = "📖"

                # Determine if this source covers the topic (above threshold)
                coverage_status = "✅" if source_score >= min_score else "⚠️"

                print(f"        {coverage_status} {source_icon} {source_name} {'[WEB]' if is_web else '[BOOK]'}")

                if is_web:
                    print(f"           └─ Best score: {source_score:.3f} | Topic: {topic_name} | {num_matches} chunks above threshold")
                else:
                    print(f"           └─ Best score: {source_score:.3f} | Ch.{chapter} | {num_matches} chunks above threshold")

                # Show text preview for sources above threshold
                if source_score >= min_score:
                    text_preview = best_source_match.get('text', '')[:100].replace('\n', ' ')
                    print(f"           └─ Preview: \"{text_preview}...\"")
        else:
            print(f"\n  ❌ Topic '{topic}': no matches found in vector store")

        # Determine if topic is covered (ANY source above threshold - books or web)
        sources_above_threshold = []
        for source_name, source_matches in matches_by_source.items():
            if source_matches[0]['score'] >= min_score:
                # Determine if this is web or book content
                source_namespace = source_matches[0].get('source_namespace', 'default')
                is_web = source_namespace == 'web_resource'

                # Get matching chunks above threshold for RAG content generation
                matching_chunks = [m for m in source_matches if m['score'] >= min_score]

                source_info = {
                    'source': source_name,
                    'confidence': source_matches[0]['score'],
                    'num_chunks': len(matching_chunks),
                    'preview': source_matches[0].get('text', '')[:200] + "...",
                    'is_web': is_web,
                    'source_type': 'web' if is_web else 'book',
                    'chunks': matching_chunks  # Include actual chunks for RAG
                }

                # Add source-specific metadata
                if is_web:
                    source_info['url'] = source_matches[0].get('metadata', {}).get('url', 'N/A')
                    source_info['topic'] = source_matches[0].get('metadata', {}).get('topic', 'N/A')
                else:
                    source_info['chapter'] = source_matches[0].get('metadata', {}).get('chapter', 'N/A')

                sources_above_threshold.append(source_info)

        if not sources_above_threshold:
            # NOT COVERED - no source meets threshold
            return {
                "covered": False,
                "topic": topic,
                "confidence": matches[0]['score'] if matches else 0.0,
                "external_resources": self._get_external_resources(topic),
                "all_sources": []  # No sources above threshold
            }

        # COVERED - return ALL sources that cover this topic (books + web)
        # Sort by confidence (best source first)
        sources_above_threshold.sort(key=lambda x: x['confidence'], reverse=True)

        return {
            "covered": True,
            "topic": topic,
            "confidence": sources_above_threshold[0]['confidence'],  # Best overall score
            "source": sources_above_threshold[0]['source'],  # Primary source (best match)
            "all_sources": sources_above_threshold,  # All sources covering this topic (books + web)
            "num_chunks": sum(s['num_chunks'] for s in sources_above_threshold),
            "top_chunk_preview": sources_above_threshold[0]['preview']
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
            keywords = topic_info.get('keywords', [])
            # Search using both topic name and keywords for better matching (keyword fallback if needed)
            coverage_map[topic_name] = {
                'coverage': self.check_topic_coverage(topic_name, keywords=keywords),
                'metadata': topic_info  # Preserve priority, keywords, tier, etc.
            }

        # Build covered topics with enriched metadata + auto-generate learning structures
        covered_topics = []
        print(f"\n🔄 Auto-generating learning structures for covered topics (cache-first)...")

        for topic_name, data in coverage_map.items():
            coverage = data['coverage']
            metadata = data['metadata']

            if coverage['covered']:
                # Get keywords for better structure generation
                keywords = metadata.get('keywords', [])
                source_books = coverage.get('all_sources', [])

                # 🚀 AUTO-GENERATE STRUCTURE (cache-first!)
                # First user: generates & caches (~$0.006)
                # Future users: instant retrieval (FREE!)
                try:
                    # Pass the coverage data directly to avoid re-querying
                    structure = self.get_or_generate_topic_structure(
                        topic_name=topic_name,
                        keywords=keywords,
                        source_books=source_books,
                        coverage_data=coverage,  # Pass original coverage with chunks!
                        db=db
                    )

                    # Include structure in covered topic data
                    topic_data = {
                        "topic": topic_name,
                        "source": coverage['source'],  # Primary source (best match)
                        "all_sources": coverage.get('all_sources', []),  # All books covering this topic
                        "confidence": coverage['confidence'],
                        # Enriched metadata
                        "priority": metadata.get('priority', 'MEDIUM'),
                        "tier": metadata.get('tier', 'EXPLICIT'),
                        "keywords": metadata.get('keywords', []),
                        "mentioned_explicitly": metadata.get('mentioned_explicitly', True),
                        # 🆕 Learning structure (weeks/sections) - cached or freshly generated!
                        "learning_structure": {
                            "weeks": structure['weeks'],
                            "estimated_hours": structure.get('estimated_hours', 20),
                            "difficulty_level": structure.get('difficulty_level', 3),
                            "cached": structure.get('cached', False)
                        }
                    }
                    covered_topics.append(topic_data)

                except Exception as e:
                    print(f"   ⚠️  Error generating structure for '{topic_name}': {e}")
                    # Add topic without structure as fallback
                    covered_topics.append({
                        "topic": topic_name,
                        "source": coverage['source'],
                        "all_sources": coverage.get('all_sources', []),
                        "confidence": coverage['confidence'],
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

    def _validate_dependencies(
        self,
        dependencies: List[Dict[str, Any]],
        stages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Validate and filter dependencies to ensure they make logical sense

        Removes:
        - Dependencies where topics don't exist in stages
        - Same-stage dependencies (topics in same stage)
        - Backwards dependencies (later stage → earlier stage)
        - Nonsensical soft skill → technical skill dependencies

        Returns: Filtered list of valid dependencies
        """
        if not dependencies or not stages:
            return []

        # Build topic → stage mapping
        topic_to_stage = {}
        for stage in stages:
            stage_num = stage.get('stage_number', 0)
            for topic in stage.get('topics', []):
                topic_name = topic.get('name', '').lower().strip()
                topic_to_stage[topic_name] = stage_num

        # Keywords for soft skills (shouldn't be prerequisites for technical topics)
        soft_skills = {'leadership', 'communication', 'teamwork', 'collaboration',
                      'presentation', 'management', 'networking'}

        valid_dependencies = []
        removed_count = 0

        for dep in dependencies:
            from_topic = dep.get('from', '').lower().strip()
            to_topic = dep.get('to', '').lower().strip()
            reason = dep.get('reason', '')

            # Check if both topics exist
            if from_topic not in topic_to_stage or to_topic not in topic_to_stage:
                print(f"  ⚠️  Removing dependency: '{dep.get('from')}' → '{dep.get('to')}' (topic not found)")
                removed_count += 1
                continue

            from_stage = topic_to_stage[from_topic]
            to_stage = topic_to_stage[to_topic]

            # Check: from_stage must be < to_stage (earlier stage)
            if from_stage >= to_stage:
                print(f"  ⚠️  Removing dependency: '{dep.get('from')}' → '{dep.get('to')}' (same/later stage)")
                removed_count += 1
                continue

            # Check: soft skill shouldn't be prerequisite for technical topic
            if any(skill in from_topic for skill in soft_skills):
                print(f"  ⚠️  Removing dependency: '{dep.get('from')}' → '{dep.get('to')}' (soft skill → technical)")
                removed_count += 1
                continue

            # Dependency is valid
            valid_dependencies.append(dep)

        if removed_count > 0:
            print(f"  ✓ Validated dependencies: kept {len(valid_dependencies)}, removed {removed_count}")

        return valid_dependencies

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
5. Dependencies MUST represent actual prerequisite relationships
6. Dependencies should cross stage boundaries (earlier stage → later stage)

DEPENDENCY RULES (CRITICAL):
✓ GOOD dependencies (prerequisite → dependent):
  - "probability theory" → "statistical modeling" (math foundation needed)
  - "linear algebra" → "machine learning" (math foundation needed)
  - "statistical modeling" → "backtesting" (must understand stats to backtest)
  - "programming" → "data analytics" (need coding skills for analysis)
  - "financial theory" → "portfolio optimization" (need theory first)

✗ BAD dependencies (these make NO SENSE):
  - "leadership" → "backtesting" (soft skill unrelated to technical skill)
  - "backtesting" → "probability theory" (backwards - stats is prerequisite!)
  - "machine learning" → "linear algebra" (backwards - math comes first!)
  - Same-stage dependencies (topics in same stage can be learned in parallel)

ONLY create dependencies where:
- The "from" topic is a TRUE prerequisite for the "to" topic
- The "from" topic appears in an EARLIER stage than the "to" topic
- The relationship is LOGICAL and PEDAGOGICAL (not random)

Common prerequisite chains in quant finance:
1. Math foundations → Statistical methods → ML/Advanced topics
2. Programming basics → Data analysis → Algorithm implementation
3. Financial theory → Quantitative models → Trading strategies
4. Probability → Statistics → Risk management

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

            # Validate and filter dependencies
            dependencies = self._validate_dependencies(dependencies, stages)

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

    def get_or_generate_topic_structure(
        self,
        topic_name: str,
        keywords: list,
        source_books: list,
        coverage_data: dict,  # Original coverage data with chunks
        db: Session
    ) -> dict:
        """
        Get cached topic structure or generate new one using GPT-4o-mini + RAG

        Args:
            topic_name: Topic name (e.g., "algorithmic strategies")
            keywords: Keywords for better RAG retrieval
            source_books: Books covering this topic
            db: Database session

        Returns:
            dict with weeks/sections structure
        """
        import hashlib
        from app.models.database import TopicStructure

        # Create unique hash for this topic (name + keywords for uniqueness)
        topic_key = f"{topic_name}|{','.join(sorted(keywords))}"
        topic_hash = hashlib.md5(topic_key.encode()).hexdigest()

        # Check cache first
        cached = db.query(TopicStructure).filter(
            TopicStructure.topic_hash == topic_hash,
            TopicStructure.is_valid == True
        ).first()

        if cached:
            # Cache hit! Increment access count
            cached.access_count += 1
            db.commit()
            print(f"✅ Cache HIT for '{topic_name}' (accessed {cached.access_count} times)")
            return {
                "weeks": cached.weeks,
                "estimated_hours": cached.estimated_hours,
                "difficulty_level": cached.difficulty_level,
                "source_books": cached.source_books,
                "cached": True
            }

        # Cache miss - generate new structure
        print(f"🔄 Cache MISS for '{topic_name}' - generating with gpt-4o-mini...")

        # Step 1: Use chunks from original coverage check (don't re-query!)
        # The coverage_data was already checked in generate_path_for_job
        chunks = []
        if coverage_data.get('covered'):
            # Get chunks from all sources
            for source_info in coverage_data.get('all_sources', []):
                chunks.extend(source_info.get('chunks', []))

        # Limit to top 20 most relevant chunks (increased for better context)
        chunks = chunks[:20]
        chunk_texts = [c.get('text', '') for c in chunks]

        print(f"   📝 Using {len(chunks)} chunks from original coverage check (score: {coverage_data.get('confidence', 0):.1%})")

        # Step 2: Generate structure using GPT-4o-mini
        structure = self._generate_topic_structure_with_llm(
            topic_name=topic_name,
            keywords=keywords,
            source_books=source_books,
            context_chunks=chunk_texts
        )

        # Step 3: Save to cache
        topic_structure = TopicStructure(
            topic_name=topic_name,
            topic_hash=topic_hash,
            weeks=structure['weeks'],
            keywords=keywords,
            source_books=source_books,
            estimated_hours=structure.get('estimated_hours', 20),
            difficulty_level=structure.get('difficulty_level', 3),
            generation_model="gpt-4o-mini",
            access_count=1
        )

        db.add(topic_structure)
        db.commit()
        db.refresh(topic_structure)

        print(f"✅ Generated and cached structure for '{topic_name}' (ID: {topic_structure.id})")

        return {
            "weeks": structure['weeks'],
            "estimated_hours": structure.get('estimated_hours', 20),
            "difficulty_level": structure.get('difficulty_level', 3),
            "source_books": source_books,
            "cached": False
        }

    def _generate_topic_structure_with_llm(
        self,
        topic_name: str,
        keywords: list,
        source_books: list,
        context_chunks: list
    ) -> dict:
        """Generate week/section structure using GPT-4o-mini + RAG context"""

        context_text = "\n\n".join(context_chunks) if context_chunks else "No specific book content available."
        books_list = ", ".join([b.get('source', 'Unknown') for b in source_books])

        system_prompt = """You are an expert curriculum designer for quantitative finance education.
Create a structured learning roadmap (weeks → sections) for interview preparation.

🚨 CRITICAL ANTI-HALLUCINATION RULES:
- ONLY use topics found in the PROVIDED BOOK CONTENT below
- DO NOT reference external books, courses, or materials
- DO NOT invent content not present in the book excerpts
- If book content is limited, create fewer sections (better to be accurate than comprehensive)
- All section topics MUST come from the actual book content provided

CRITICAL REQUIREMENTS:
1. Structure into 2-4 weeks of learning
2. Each week has 4-6 sections (NOT 1-2!) - this is a parent topic that needs detailed breakdown
3. Each section is a focused sub-topic (45-90 min of study)
4. Base structure EXCLUSIVELY on PROVIDED BOOK CONTENT - don't invent topics not in the books
5. Order sections from foundational → advanced
6. Include practical examples and interview relevance
7. Cover the breadth of the parent topic - for "Python programming", include syntax, data structures, libraries, etc.

QUALITY STANDARDS - Section Titles Must Be SPECIFIC:
✅ GOOD: "NumPy Arrays and Vectorization", "Pandas DataFrame Operations and Indexing"
✅ GOOD: "Linear Regression: OLS, Assumptions, and Diagnostics", "Decision Trees and Random Forests"
✅ GOOD: "Ridge vs Lasso: L1 vs L2 Regularization", "ARIMA Models for Financial Time Series"
❌ BAD: "Introduction to Python", "Basics of Programming", "Overview of ML", "Fundamentals"
❌ BAD: Generic topic names without specifics
❌ BAD: Single generic section for a complex topic

SECTION BREADTH - Example for "Python programming" parent topic:
Week 1: Python Fundamentals
  - "Basic Syntax: Variables, Types, and Control Flow"
  - "Data Structures: Lists, Tuples, Dicts, and Sets"
  - "Functions, Lambdas, and Comprehensions"
  - "Object-Oriented Programming: Classes and Inheritance"
Week 2: Scientific Computing in Python
  - "NumPy Arrays and Vectorization"
  - "Pandas DataFrames: Loading, Filtering, and Aggregation"
  - "Matplotlib and Seaborn for Data Visualization"
  - "SciPy for Scientific Computing"

Use concrete mathematical formulas, algorithm names, library functions, and specific techniques from the book content.
Make section titles immediately actionable and interview-focused.

Return ONLY valid JSON (no markdown, no extra text):
{
  "weeks": [
    {
      "weekNumber": 1,
      "title": "Week title",
      "sections": [
        {
          "id": "1.1",
          "title": "Section title",
          "topics": ["Key concept 1", "Key concept 2", "Key concept 3"],
          "estimatedMinutes": 60,
          "interviewRelevance": "Why this appears in interviews"
        }
      ]
    }
  ],
  "estimated_hours": 20,
  "difficulty_level": 3
}"""

        user_prompt = f"""Topic: {topic_name}
Keywords: {', '.join(keywords)}
Source Books: {books_list}

Book Content (use this to structure your roadmap):
{context_text}

Create a practical learning roadmap for someone preparing for quant interviews.
Focus on concepts actually covered in the provided book content.
Return valid JSON only."""

        response = self.llm_service.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent, detailed structures
            max_tokens=2500,  # Increased for more detailed content
            response_format={"type": "json_object"}
        )

        import json
        try:
            structure = json.loads(response.choices[0].message.content)
            return structure
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON decode error: {e}")
            # Fallback structure
            return {
                "weeks": [
                    {
                        "weekNumber": 1,
                        "title": f"Introduction to {topic_name}",
                        "sections": [
                            {
                                "id": "1.1",
                                "title": f"{topic_name} Fundamentals",
                                "topics": keywords[:3],
                                "estimatedMinutes": 90,
                                "interviewRelevance": "Core concept for interviews"
                            }
                        ]
                    }
                ],
                "estimated_hours": 15,
                "difficulty_level": 3
            }

    def get_or_generate_section_content(
        self,
        topic_name: str,
        section_id: str,
        section_title: str,
        topic_keywords: list,
        db: Session
    ) -> dict:
        """
        Get cached section content or generate new using Claude/GPT-4 + RAG

        Similar to get_or_generate_topic_structure but for individual section content
        Uses Claude Sonnet 3.5 for premium quality (or GPT-4 as fallback)

        Returns:
            {
                "content": "markdown content with LaTeX",
                "estimated_minutes": 45,
                "cached": True/False,
                "generation_model": "claude-3-5-sonnet"
            }
        """
        import hashlib
        from app.models.database import SectionContent

        # Create unique hash for this section
        content_key = f"{topic_name}|{section_id}|{section_title}"
        content_hash = hashlib.md5(content_key.encode()).hexdigest()

        # Check cache first
        cached = db.query(SectionContent).filter(
            SectionContent.content_hash == content_hash,
            SectionContent.is_valid == True
        ).first()

        if cached:
            # Cache hit! Increment access count
            cached.access_count += 1
            db.commit()
            print(f"✅ Cache HIT for section '{topic_name} - {section_id}' (accessed {cached.access_count} times)")

            import json
            return {
                "sectionTitle": cached.section_title,
                "estimatedTime": f"{cached.estimated_minutes or 45} minutes",
                "content": json.loads(cached.content),  # Parse JSON string back to dict
                "cached": True,
                "generation_model": cached.generation_model
            }

        # Cache miss - generate new content
        print(f"🔄 Cache MISS for section '{topic_name} - {section_id}' - generating with Claude/GPT-4...")

        # Step 1: Retrieve relevant chunks from RAG
        search_query = f"{topic_name} {section_title} {' '.join(topic_keywords[:3])}"
        coverage = self.check_topic_coverage(search_query)

        chunks = []
        if coverage['covered']:
            for source_info in coverage.get('all_sources', []):
                chunks.extend(source_info.get('chunks', []))

        # Limit to top 15 most relevant chunks
        chunks = chunks[:15]
        chunk_texts = [c.get('text', '') for c in chunks]

        # Step 2: Generate rich content using Claude (or GPT-4) in validated JSON structure
        content_dict = self.llm_service.generate_rich_section_content(
            topic_name=topic_name,
            section_title=section_title,
            section_id=section_id,
            context_chunks=chunk_texts,
            use_claude=True  # Use Claude by default for quality
        )

        # Determine which model was used
        generation_model = "claude-3-5-sonnet" if self.llm_service.claude_client else "gpt-4-turbo"

        # Estimate reading time from content structure
        intro_length = len(content_dict.get('introduction', ''))
        sections_length = sum(len(s.get('content', '')) for s in content_dict.get('sections', []))
        total_length = intro_length + sections_length
        estimated_minutes = max(30, min(90, total_length // 1000))  # 30-90 min range

        # Step 3: Save to cache (handle duplicate gracefully)
        import json
        try:
            section_content = SectionContent(
                topic_name=topic_name,
                section_id=section_id,
                section_title=section_title,
                content_hash=content_hash,
                content=json.dumps(content_dict),  # Store as JSON string
                topic_keywords=topic_keywords,
                source_chunks_count=len(chunks),
                estimated_minutes=estimated_minutes,
                generation_model=generation_model,
                access_count=1
            )

            db.add(section_content)
            db.commit()
            db.refresh(section_content)

            print(f"✅ Generated and cached section content ({len(chunks)} chunks, ~{estimated_minutes} min)")

        except Exception as e:
            if "duplicate key" in str(e):
                print(f"⚠️  Content already exists (race condition), fetching from cache...")
                db.rollback()
                # Fetch the existing content
                cached = db.query(SectionContent).filter(
                    SectionContent.content_hash == content_hash
                ).first()
                if cached:
                    cached.access_count += 1
                    db.commit()
                    return {
                        "sectionTitle": section_title,
                        "estimatedTime": f"{cached.estimated_minutes} minutes",
                        "content": json.loads(cached.content),
                        "cached": True,
                        "generation_model": cached.generation_model
                    }
            else:
                raise e

        return {
            "sectionTitle": section_title,
            "estimatedTime": f"{estimated_minutes} minutes",
            "content": content_dict,
            "cached": False,
            "generation_model": generation_model
        }


# Singleton instance
learning_path_service = LearningPathService()
