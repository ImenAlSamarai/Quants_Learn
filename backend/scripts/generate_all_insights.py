"""
Master script to generate insights for ALL indexed topics

Runs all insight generation scripts in sequence:
- Chapter 3: Linear Regression methods
- Chapter 4: Classification methods
- Chapter 7: Model Assessment
- Chapters 9-10: Trees and Boosting
- Chapter 14: Unsupervised Learning
- Chapter 15: Random Forests
"""

import subprocess
import sys
import time


def run_script(script_name: str, description: str):
    """Run a single insight generation script"""
    print("\n" + "=" * 80)
    print(f"Running: {description}")
    print("=" * 80)

    start_time = time.time()

    try:
        result = subprocess.run(
            [sys.executable, f"scripts/{script_name}"],
            cwd=".",
            capture_output=False,
            text=True
        )

        elapsed_time = time.time() - start_time

        if result.returncode == 0:
            print(f"\n✓ {description} completed in {elapsed_time:.1f} seconds")
            return True
        else:
            print(f"\n✗ {description} failed with return code {result.returncode}")
            return False

    except Exception as e:
        print(f"\n✗ Error running {script_name}: {e}")
        return False


def main():
    print("=" * 80)
    print("GENERATE INSIGHTS FOR ALL TOPICS")
    print("=" * 80)
    print("\nThis will generate practitioner insights for all indexed ESL topics.")
    print("Estimated time: 5-10 minutes")
    print("Estimated cost: ~$0.10-0.20 (OpenAI API)")
    print()

    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return

    overall_start = time.time()

    scripts = [
        ("generate_chapter3_insights.py", "Chapter 3 (Linear Regression)"),
        ("generate_chapter4_insights.py", "Chapter 4 (Classification)"),
        ("generate_chapter7_insights.py", "Chapter 7 (Model Assessment)"),
        ("generate_chapters9_10_insights.py", "Chapters 9-10 (Trees & Boosting)"),
        ("generate_chapter14_insights.py", "Chapter 14 (Unsupervised Learning)"),
        ("generate_chapter15_insights.py", "Chapter 15 (Random Forests)"),
    ]

    results = []

    for script, description in scripts:
        success = run_script(script, description)
        results.append((description, success))

    # Summary
    overall_time = time.time() - overall_start

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nTotal time: {overall_time / 60:.1f} minutes")
    print("\nResults:")

    for description, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {description}")

    total = len(results)
    successful = sum(1 for _, success in results if success)

    print(f"\nSuccess rate: {successful}/{total}")

    if successful == total:
        print("\n🎉 All insights generated successfully!")
        print("\nNext steps:")
        print("  1. Start backend: uvicorn app.main:app --reload")
        print("  2. Start frontend: npm run dev")
        print("  3. Test insights button on any topic!")
    else:
        print("\n⚠️  Some scripts failed. Check errors above.")
        print("You can re-run individual scripts:")
        for description, success in results:
            if not success:
                print(f"  python scripts/generate_{description.lower().replace(' ', '_')}_insights.py")


if __name__ == "__main__":
    main()
