"""
Smoke test for the Gemini-backed summarization in AIAnalyzer.
Run from the project root:  python scripts/test_gemini_summarizer.py
"""
import sys
import os

# Make sure project root is on the path so `app.*` imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.ai_analyzer import AIAnalyzer

SAMPLE_COMPLAINTS = [
    (
        "Water Leak",
        (
            "There is a massive water pipe burst on Oak Street near the intersection with "
            "Elm Avenue. Water has been flooding the road since yesterday morning and is now "
            "entering the basements of several houses. The water pressure in the entire "
            "neighbourhood has also dropped significantly."
        ),
    ),
    (
        "Pothole",
        (
            "The pothole on Main Street in front of number 45 has been there for over three "
            "months now. It is at least 30 cm deep and has already caused two cyclists to fall. "
            "A car tyre was also damaged last week. It is becoming very dangerous."
        ),
    ),
    (
        "Illegal Dumping",
        (
            "Someone has dumped a large pile of construction rubble, old furniture, and black "
            "bin bags on the corner of Green Lane and Park Road overnight. The smell is "
            "terrible and it is blocking part of the pavement so pedestrians have to walk in "
            "the road."
        ),
    ),
]


def main():
    analyzer = AIAnalyzer()

    print("\n" + "=" * 70)
    print("  Groq Summarization Smoke Test — llama-3.3-70b-versatile")
    print("=" * 70)

    for title, description in SAMPLE_COMPLAINTS:
        print(f"\n[{title}]")
        print(f"  Input  : {description[:80]}...")
        summary, fallback = analyzer.summarize(description)
        status = "FALLBACK" if fallback else "GROQ"
        print(f"  Summary: {summary}")
        print(f"  Source : {status}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
