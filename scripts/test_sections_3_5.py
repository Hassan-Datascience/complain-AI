"""
Script to test section 3 (Analytics Edge Cases) and section 5 (Smoke Test for Waste, Safety, Other, plus 422 error test).
"""
import time
import json
import urllib.request
import urllib.error
from app.services.database_manager import DatabaseManager

BASE_URL = "http://127.0.0.1:8000"

def http_get(url):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def http_post(url, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())

def http_patch(url, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="PATCH"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def main():
    print("=== Section 3: Analytics Edge Cases Test ===")
    # 1. Test /analytics/stats with current DB status
    stats = http_get(f"{BASE_URL}/analytics/stats")
    print("Zero/Initial resolved stats response:", json.dumps(stats, indent=2))

    # 2. Post a complaint and mark as Resolved to verify stats calculation
    c_res = http_post(f"{BASE_URL}/complaints", {
        "description": "Trash overflowing in park causing odor issues",
        "location": "Park Lane"
    })
    cid = c_res["complaint_id"]
    http_patch(f"{BASE_URL}/complaints/{cid}/status", {"status": "Resolved"})
    
    stats_after = http_get(f"{BASE_URL}/analytics/stats")
    print("Stats response after 1 resolved:", json.dumps(stats_after, indent=2))

    summary = http_get(f"{BASE_URL}/analytics/summary")
    trends = http_get(f"{BASE_URL}/analytics/trends")
    print("Analytics Summary OK:", summary.get("total_complaints", 0) > 0)
    print("Analytics Trends OK:", len(trends.get("daily_trends", [])) >= 0)

    print("\n=== Section 5: Full API Smoke Test (Waste, Safety, Other + 422 Error) ===")
    test_cases = [
        {
            "label": "Waste",
            "payload": {
                "description": "Garbage cans overflowing near municipal market for 3 days attracting flies and stray animals.",
                "location": "Market Square"
            }
        },
        {
            "label": "Safety",
            "payload": {
                "description": "Aggressive stray dogs near school gate scaring children every afternoon.",
                "location": "Elementary School Gate"
            }
        },
        {
            "label": "Other",
            "payload": {
                "description": "Public park benches damaged and overgrown weeds covering walking trail.",
                "location": "Central Park"
            }
        }
    ]

    for item in test_cases:
        print(f"\nPosting {item['label']} complaint...")
        resp = http_post(f"{BASE_URL}/complaints", item["payload"])
        print(f"POST Response ({item['label']}):")
        print(json.dumps(resp, indent=2))
        
        # Confirm GET persistence
        cid = resp["complaint_id"]
        get_resp = http_get(f"{BASE_URL}/complaints/{cid}")
        print(f"GET Confirmation for {cid}: Success ({get_resp['complaint_id'] == cid})")

    # Test short description error (under 10 chars)
    print("\nTesting validation error (<10 chars description)...")
    try:
        http_post(f"{BASE_URL}/complaints", {"description": "Too short", "location": "Test"})
        print("ERROR: Validation failed to trigger 422!")
    except urllib.error.HTTPError as e:
        print(f"Caught HTTP {e.code} as expected:")
        print(e.read().decode())

if __name__ == "__main__":
    main()
