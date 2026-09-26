"""
ROAM — Evaluation Runner
Runs all test cases and aggregates results into EvaluationResult.
"""

from __future__ import annotations

from datetime import datetime

from schemas.models import EvaluationResult
from evaluation.test_suite import get_all_tests


def run_all_tests() -> EvaluationResult:
    """Run all evaluation tests and aggregate results."""
    test_functions = get_all_tests()
    test_cases = []

    for test_fn in test_functions:
        try:
            result = test_fn()
            test_cases.append(result)
        except Exception as e:
            from schemas.models import EvaluationTestCase
            test_cases.append(EvaluationTestCase(
                name=test_fn.__name__,
                category="error",
                description=f"Test crashed: {e}",
                passed=False,
                score=0,
                details=str(e),
                errors=[str(e)],
            ))

    # Aggregate
    total = len(test_cases)
    passed = sum(1 for tc in test_cases if tc.passed)
    failed = total - passed

    # Category scores
    categories: dict[str, list[float]] = {}
    for tc in test_cases:
        if tc.category not in categories:
            categories[tc.category] = []
        categories[tc.category].append(tc.score)

    category_scores = {
        cat: round(sum(scores) / len(scores) * 100, 1)
        for cat, scores in categories.items()
    }

    overall = round(sum(tc.score for tc in test_cases) / max(total, 1) * 100, 1)

    return EvaluationResult(
        total_tests=total,
        passed=passed,
        failed=failed,
        categories=category_scores,
        test_cases=test_cases,
        overall_score=overall,
        run_timestamp=datetime.utcnow().isoformat(),
    )
