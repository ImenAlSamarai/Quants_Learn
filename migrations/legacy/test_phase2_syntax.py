"""
Phase 2 Syntax Verification Test

Tests that all Python files in Phase 2 have valid syntax.
This test doesn't require any dependencies or running server.

Run: python backend/test_phase2_syntax.py
"""

import py_compile
import sys
from pathlib import Path

print("=" * 60)
print("PHASE 2 SYNTAX VERIFICATION")
print("=" * 60)

# Files to check
files_to_check = [
    "backend/app/models/database.py",
    "backend/app/models/schemas.py",
    "backend/app/services/learning_path_service.py",
    "backend/app/services/llm_service.py",
    "backend/app/routes/content.py",
    "backend/app/routes/users.py",
    "backend/management/commands/migrate_to_job_based.py",
]

passed = 0
failed = 0

print("\nChecking Python syntax...")
print("-" * 60)

for file_path in files_to_check:
    try:
        py_compile.compile(file_path, doraise=True)
        print(f"✓ {file_path}")
        passed += 1
    except py_compile.PyCompileError as e:
        print(f"✗ {file_path}")
        print(f"  Error: {e}")
        failed += 1

print("-" * 60)
print(f"\nResults: {passed} passed, {failed} failed")

if failed > 0:
    print("\n✗ SYNTAX CHECK FAILED")
    sys.exit(1)
else:
    print("\n✅ ALL SYNTAX CHECKS PASSED")
    print("\nPhase 2 Files Verified:")
    print("  ✓ database.py - Schema changes")
    print("  ✓ schemas.py - New Pydantic models")
    print("  ✓ learning_path_service.py - Job parsing & path generation")
    print("  ✓ llm_service.py - Job-based content generation")
    print("  ✓ content.py - Updated routes with job support")
    print("  ✓ users.py - New job-based endpoints")
    print("  ✓ migrate_to_job_based.py - Database migration")
    print("\n🎯 Phase 2 Ready for Integration Testing")
    sys.exit(0)
