#!/usr/bin/env python3
"""
Simple node indexing script (without Pinecone)

This script creates nodes in PostgreSQL without indexing content into Pinecone.
Use this when you want to quickly populate the database with node structure.

Usage:
    python scripts/index_nodes_simple.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base, Node
from app.config.settings import settings


def main():
    print("=" * 60)
    print("SIMPLE NODE INDEXING")
    print("=" * 60)
    print()
    print("Creating database tables...")

    # Create engine and session
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Clear existing data by dropping and recreating all tables
        print("Clearing existing data...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("Database tables recreated successfully!")

        print("Creating nodes...")

        # Linear Algebra nodes
        la_root = Node(
            title="Linear Algebra",
            slug="linear-algebra",
            category="linear_algebra",
            description="Mathematical study of vectors, matrices, and linear transformations",
            difficulty_level=2,
            x_position=0,
            y_position=0,
            color="#3b82f6",
            icon="🔷",
            content_path="../content/linear_algebra/overview.md"
        )
        db.add(la_root)
        db.commit()
        db.refresh(la_root)

        vectors = Node(
            title="Vectors and Spaces",
            slug="vectors-and-spaces",
            category="linear_algebra",
            subcategory="vectors",
            description="Vector operations, spaces, and properties",
            difficulty_level=1,
            x_position=-2,
            y_position=2,
            color="#60a5fa",
            icon="➡️",
            content_path="../content/linear_algebra/vectors.md"
        )
        vectors.parents.append(la_root)
        db.add(vectors)
        db.commit()
        db.refresh(vectors)

        matrices = Node(
            title="Matrix Operations",
            slug="matrix-operations",
            category="linear_algebra",
            subcategory="matrices",
            description="Matrix multiplication, inverses, and properties",
            difficulty_level=2,
            x_position=0,
            y_position=2,
            color="#60a5fa",
            icon="⊞",
            content_path="../content/linear_algebra/matrices.md"
        )
        matrices.parents.extend([la_root, vectors])
        db.add(matrices)
        db.commit()
        db.refresh(matrices)

        transforms = Node(
            title="Linear Transformations",
            slug="linear-transformations",
            category="linear_algebra",
            subcategory="transformations",
            description="Linear maps and their matrix representations",
            difficulty_level=3,
            x_position=2,
            y_position=2,
            color="#60a5fa",
            icon="🔄",
            content_path="../content/linear_algebra/transformations.md"
        )
        transforms.parents.extend([la_root, matrices])
        db.add(transforms)
        db.commit()
        db.refresh(transforms)

        eigen = Node(
            title="Eigenvalues and Eigenvectors",
            slug="eigenvalues-and-eigenvectors",
            category="linear_algebra",
            subcategory="eigenvalues",
            description="Spectral properties and diagonalization",
            difficulty_level=3,
            x_position=-2,
            y_position=4,
            color="#2563eb",
            icon="λ",
            content_path="../content/linear_algebra/eigenvalues.md"
        )
        eigen.parents.extend([matrices, transforms])
        db.add(eigen)
        db.commit()
        db.refresh(eigen)

        svd = Node(
            title="SVD and Decompositions",
            slug="svd-and-decompositions",
            category="linear_algebra",
            subcategory="decomposition",
            description="Singular Value Decomposition, PCA, and matrix factorization",
            difficulty_level=4,
            x_position=0,
            y_position=4,
            color="#2563eb",
            icon="🔸",
            content_path="../content/linear_algebra/svd.md"
        )
        svd.parents.append(eigen)
        db.add(svd)
        db.commit()
        db.refresh(svd)

        # Calculus nodes
        calc_root = Node(
            title="Calculus",
            slug="calculus",
            category="calculus",
            description="Mathematical study of continuous change, rates, and accumulation",
            difficulty_level=2,
            x_position=6,
            y_position=0,
            color="#10b981",
            icon="∫",
            content_path="../content/calculus/overview.md"
        )
        db.add(calc_root)
        db.commit()
        db.refresh(calc_root)

        limits = Node(
            title="Limits and Continuity",
            slug="limits-and-continuity",
            category="calculus",
            subcategory="limits",
            description="Foundation of calculus: behavior as values approach points",
            difficulty_level=1,
            x_position=4,
            y_position=2,
            color="#34d399",
            icon="→",
            content_path="../content/calculus/limits.md"
        )
        limits.parents.append(calc_root)
        db.add(limits)
        db.commit()
        db.refresh(limits)

        derivatives = Node(
            title="Derivatives",
            slug="derivatives",
            category="calculus",
            subcategory="derivatives",
            description="Instantaneous rates of change and optimization",
            difficulty_level=2,
            x_position=6,
            y_position=2,
            color="#34d399",
            icon="d/dx",
            content_path="../content/calculus/derivatives.md"
        )
        derivatives.parents.extend([calc_root, limits])
        db.add(derivatives)
        db.commit()
        db.refresh(derivatives)

        integrals = Node(
            title="Integration",
            slug="integration",
            category="calculus",
            subcategory="integrals",
            description="Accumulation and areas under curves",
            difficulty_level=2,
            x_position=8,
            y_position=2,
            color="#34d399",
            icon="∫",
            content_path="../content/calculus/integrals.md"
        )
        integrals.parents.extend([calc_root, derivatives])
        db.add(integrals)
        db.commit()
        db.refresh(integrals)

        multivariable = Node(
            title="Multivariable Calculus",
            slug="multivariable-calculus",
            category="calculus",
            subcategory="multivariable",
            description="Calculus in multiple dimensions: gradients and optimization",
            difficulty_level=3,
            x_position=6,
            y_position=4,
            color="#059669",
            icon="∇",
            content_path="../content/calculus/multivariable.md"
        )
        multivariable.parents.extend([derivatives, integrals])
        db.add(multivariable)
        db.commit()
        db.refresh(multivariable)

        # Probability nodes
        prob_root = Node(
            title="Probability Theory",
            slug="probability-theory",
            category="probability",
            description="Mathematical framework for quantifying uncertainty",
            difficulty_level=2,
            x_position=12,
            y_position=0,
            color="#f59e0b",
            icon="🎲",
            content_path="../content/probability/overview.md"
        )
        db.add(prob_root)
        db.commit()
        db.refresh(prob_root)

        prob_foundations = Node(
            title="Probability Foundations",
            slug="probability-foundations",
            category="probability",
            subcategory="foundations",
            description="Sample spaces, events, axioms, and conditional probability",
            difficulty_level=1,
            x_position=10,
            y_position=2,
            color="#fbbf24",
            icon="Ω",
            content_path="../content/probability/foundations.md"
        )
        prob_foundations.parents.append(prob_root)
        db.add(prob_foundations)
        db.commit()
        db.refresh(prob_foundations)

        random_vars = Node(
            title="Random Variables and Distributions",
            slug="random-variables-and-distributions",
            category="probability",
            subcategory="random_variables",
            description="Discrete and continuous distributions, transformations",
            difficulty_level=2,
            x_position=12,
            y_position=2,
            color="#fbbf24",
            icon="X",
            content_path="../content/probability/random_variables.md"
        )
        random_vars.parents.extend([prob_root, prob_foundations])
        db.add(random_vars)
        db.commit()
        db.refresh(random_vars)

        expectation = Node(
            title="Expectation and Moments",
            slug="expectation-and-moments",
            category="probability",
            subcategory="expectation",
            description="Expected values, variance, and characterizing distributions",
            difficulty_level=2,
            x_position=14,
            y_position=2,
            color="#fbbf24",
            icon="E[X]",
            content_path="../content/probability/expectation.md"
        )
        expectation.parents.extend([prob_root, random_vars])
        db.add(expectation)
        db.commit()
        db.refresh(expectation)

        # Statistics nodes
        stats_root = Node(
            title="Statistics",
            slug="statistics",
            category="statistics",
            description="Analyzing data and making inferences under uncertainty",
            difficulty_level=2,
            x_position=18,
            y_position=0,
            color="#8b5cf6",
            icon="📊",
            content_path="../content/statistics/overview.md"
        )
        db.add(stats_root)
        db.commit()
        db.refresh(stats_root)

        inference = Node(
            title="Statistical Inference",
            slug="statistical-inference",
            category="statistics",
            subcategory="inference",
            description="Estimation, confidence intervals, and hypothesis testing",
            difficulty_level=2,
            x_position=16,
            y_position=2,
            color="#a78bfa",
            icon="CI",
            content_path="../content/statistics/inference.md"
        )
        inference.parents.extend([stats_root, expectation])
        db.add(inference)
        db.commit()
        db.refresh(inference)

        regression = Node(
            title="Regression Analysis",
            slug="regression-analysis",
            category="statistics",
            subcategory="regression",
            description="Modeling relationships between variables",
            difficulty_level=3,
            x_position=18,
            y_position=2,
            color="#a78bfa",
            icon="β",
            content_path="../content/statistics/regression.md"
        )
        regression.parents.extend([stats_root, inference, multivariable])
        db.add(regression)
        db.commit()
        db.refresh(regression)

        timeseries = Node(
            title="Time Series Analysis",
            slug="time-series-analysis",
            category="statistics",
            subcategory="time_series",
            description="ARMA, GARCH, and forecasting sequential data",
            difficulty_level=3,
            x_position=20,
            y_position=2,
            color="#a78bfa",
            icon="📈",
            content_path="../content/statistics/time_series.md"
        )
        timeseries.parents.extend([stats_root, regression])
        db.add(timeseries)
        db.commit()
        db.refresh(timeseries)

        print("\n" + "=" * 60)
        print("Content indexing completed successfully!")
        print(f"Total nodes indexed: 20")
        print("\nCategories:")
        print("  - Linear Algebra: 6 nodes")
        print("  - Calculus: 5 nodes")
        print("  - Probability: 4 nodes")
        print("  - Statistics: 4 nodes")
        print("\nNext steps:")
        print("1. Start the backend server")
        print("2. View mind map at http://localhost:8000/api/nodes/mindmap")
        print("=" * 60)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
