"""
Master script to index ALL Deep Learning topics

Runs indexing scripts in sequence:
- Chapters 7-8: Training (Gradient Descent, Backpropagation, Optimizers) - 4 topics
- Chapter 6: Deep Neural Networks fundamentals - 4 topics
- Chapter 10: Convolutional Networks - 4 topics
- Chapter 12: Transformers - 4 topics

Total: 16 Deep Learning topics to add to Machine Learning category
"""

import subprocess
import sys
import time


def run_script(script_name: str, description: str):
    """Run a single indexing script"""
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
    print("INDEX ALL DEEP LEARNING TOPICS")
    print("=" * 80)
    print("\nThis will index Deep Learning topics from Bishop's book:")
    print("  - Chapters 7-8: Training (4 topics)")
    print("  - Chapter 6: Fundamentals (4 topics)")
    print("  - Chapter 10: CNNs (4 topics)")
    print("  - Chapter 12: Transformers (4 topics)")
    print("\nTotal: 16 new Deep Learning topics")
    print("Estimated time: 5-10 minutes")
    print("Estimated cost: ~$0.50-1.00 (Pinecone + OpenAI embeddings)")
    print()

    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return

    overall_start = time.time()

    scripts = [
        ("index_dl_chapters7_8.py", "Chapters 7-8 (Training)"),
        ("index_dl_chapter6.py", "Chapter 6 (Deep Neural Networks)"),
        ("index_dl_chapter10.py", "Chapter 10 (Convolutional Networks)"),
        ("index_dl_chapter12.py", "Chapter 12 (Transformers)"),
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
        print("\n🎉 All Deep Learning topics indexed successfully!")
        print("\nTopics added (16 total):")
        print("\nTraining (4):")
        print("  - Gradient Descent and Optimization")
        print("  - Backpropagation Algorithm")
        print("  - Advanced Optimizers (Adam, RMSprop, Momentum)")
        print("  - Batch Normalization and Layer Normalization")
        print("\nFundamentals (4):")
        print("  - Feedforward Neural Networks")
        print("  - Activation Functions")
        print("  - Output Units and Loss Functions")
        print("  - Universal Approximation")
        print("\nCNNs (4):")
        print("  - Convolutional Neural Networks (CNNs)")
        print("  - Pooling and Subsampling")
        print("  - CNN Architectures (LeNet, AlexNet, VGG, ResNet)")
        print("  - Transfer Learning and Fine-Tuning")
        print("\nTransformers (4):")
        print("  - Attention Mechanisms")
        print("  - Self-Attention and Multi-Head Attention")
        print("  - Transformer Architecture")
        print("  - Transformer Language Models (BERT, GPT)")
        print("\nNext steps:")
        print("  1. Verify: python scripts/check_indexed_content.py | grep -i 'neural\\|cnn\\|transform'")
        print("  2. Generate insights: python scripts/generate_all_dl_insights.py")
        print("  3. Test frontend: uvicorn app.main:app --reload (then npm run dev)")
    else:
        print("\n⚠️  Some scripts failed. Check errors above.")
        print("You can re-run individual scripts:")
        for description, success in results:
            if not success:
                script_name = description.lower().replace(" ", "_").replace("(", "").replace(")", "")
                print(f"  python scripts/index_{script_name}.py")


if __name__ == "__main__":
    main()
