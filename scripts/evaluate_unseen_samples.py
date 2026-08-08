import os
import sys
from app.services.ai_analyzer import AIAnalyzer

def evaluate_unseen_comparison():
    analyzer = AIAnalyzer()

    # Pre-recorded old priority predictions (from the 60% accuracy run)
    old_results = {
        1: ("Critical", True),   # Match: YES
        2: ("Low", False),       # Match: NO
        3: ("Low", False),       # Match: NO
        4: ("Medium", False),    # Match: NO
        5: ("Medium", False),    # Match: NO
        6: ("Low", True),        # Match: YES
        7: ("Critical", True),   # Match: YES
        8: ("Low", True),        # Match: YES
        9: ("Medium", True),     # Match: YES
        10: ("High", True)       # Match: YES
    }

    new_test_cases = [
        {
            "id": 1,
            "text": "A massive sinkhole has suddenly opened up right outside the emergency room entrance of St. Mary's Hospital, swallowing part of a delivery van.",
            "ground_truth_category": "Road",
            "ground_truth_priority": "Critical"
        },
        {
            "id": 2,
            "text": "Water coming from our bathroom faucets has a distinct oily sheen and smells like gasoline since yesterday morning.",
            "ground_truth_category": "Water/Drainage",
            "ground_truth_priority": "Critical"
        },
        {
            "id": 3,
            "text": "Dozens of plastic trash bags have been ripped open by stray animals near the elementary school, leaving rotting meat and maggots across the sidewalk.",
            "ground_truth_category": "Waste",
            "ground_truth_priority": "High"
        },
        {
            "id": 4,
            "text": "A high-voltage transformer near the commercial plaza is buzzing intensely and emitting dark grey smoke.",
            "ground_truth_category": "Electricity",
            "ground_truth_priority": "Critical"
        },
        {
            "id": 5,
            "text": "An unlit, open construction pit along the footbridge has no warning sign or barricade, and a pedestrian stumbled into it last night.",
            "ground_truth_category": "Safety",
            "ground_truth_priority": "Critical"
        },
        {
            "id": 6,
            "text": "The municipal library's public garden has become overgrown with dandelions and thistle weeds, obstructing the ornamental bench.",
            "ground_truth_category": "Other",
            "ground_truth_priority": "Low"
        },
        {
            "id": 7,
            "text": "Sub-surface storm sewer pipe collapsed under 3rd Avenue, causing heavy rainwater to backup into 12 residential basements.",
            "ground_truth_category": "Water/Drainage",
            "ground_truth_priority": "Critical"
        },
        {
            "id": 8,
            "text": "Streetlight pole #402 on Maple Drive is completely blacked out, leaving the entire cul-de-sac pitch dark after sunset.",
            "ground_truth_category": "Electricity",
            "ground_truth_priority": "Low"
        },
        {
            "id": 9,
            "text": "Someone dumped five old CRT monitors and discarded computer towers in the creek behind the community center.",
            "ground_truth_category": "Waste",
            "ground_truth_priority": "Medium"
        },
        {
            "id": 10,
            "text": "Noise from illegal late-night drag racing on the bypass road is keeping residents awake every weekend past 3 AM.",
            "ground_truth_category": "Safety",
            "ground_truth_priority": "High"
        }
    ]

    print("\n" + "="*120)
    print("           PRIORITY MODEL EVALUATION: BEFORE VS. AFTER RETRAINING ON 10 UNSEEN COMPLAINTS")
    print("="*120)

    old_correct_count = 6
    new_correct_count = 0

    print(f"{'#':<3} | {'Ground Truth':<15} | {'Old Prediction':<18} | {'New Prediction':<18} | {'Old Match':<10} | {'New Match':<10} | {'New Conf.':<8}")
    print("-" * 120)

    for item in new_test_cases:
        res = analyzer.analyze(item["text"])
        tid = item["id"]
        gt_prio = item["ground_truth_priority"]
        old_pred, old_match = old_results[tid]
        new_pred = res["priority"]
        new_match = (new_pred == gt_prio)

        if new_match:
            new_correct_count += 1

        old_match_str = "YES" if old_match else "NO"
        new_match_str = "YES" if new_match else "NO"

        print(f"{tid:<3} | {gt_prio:<15} | {old_pred:<18} | {new_pred:<18} | {old_match_str:<10} | {new_match_str:<10} | {res['ai_confidence']:<8.2f}")

    print("="*120)
    print(f"OLD PRIORITY ACCURACY : {old_correct_count}/10 ({old_correct_count/10*100:.1f}%)")
    print(f"NEW PRIORITY ACCURACY : {new_correct_count}/10 ({new_correct_count/10*100:.1f}%)")
    print("="*120 + "\n")

if __name__ == "__main__":
    evaluate_unseen_comparison()
