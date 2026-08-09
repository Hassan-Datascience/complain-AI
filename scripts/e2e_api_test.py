"""
Full end-to-end API test for AI Smart Civic Services.
POSTs 3 complaints (Water, Electricity, Road), prints the full JSON response,
then GETs each by ID and confirms persistence.

Run from project root:  python scripts/e2e_api_test.py
"""
import json
import sys
import time
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

COMPLAINTS = [
    {
        "label": "Water Leak",
        "payload": {
            "description": (
                "There is a burst water pipe on Maple Avenue near house number 12. "
                "Water has been gushing onto the street since early this morning, "
                "flooding the pavement and the front gardens of at least four properties. "
                "The water pressure in the surrounding streets has dropped to almost nothing."
            ),
            "location": "Maple Avenue, near house 12",
            "date": "2026-08-09T03:30:00",
        },
    },
    {
        "label": "Electricity Fault",
        "payload": {
            "description": (
                "The street lights on Cedar Road between the post office and the school "
                "have been completely out for five days. The area is extremely dark at night "
                "and residents are worried about safety and potential accidents. "
                "A transformer box on the corner is also making a loud buzzing sound."
            ),
            "location": "Cedar Road, between post office and school",
            "date": "2026-08-09T03:30:00",
        },
    },
    {
        "label": "Road Damage",
        "payload": {
            "description": (
                "A large section of tarmac has collapsed on the junction of High Street "
                "and Bridge Lane creating a crater roughly one metre wide and half a metre deep. "
                "It is blocking one full lane of traffic and has already damaged at least "
                "two cars. The road surface around it is also cracking and could spread."
            ),
            "location": "Junction of High Street and Bridge Lane",
            "date": "2026-08-09T03:30:00",
        },
    },
]


def http_post(url, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def http_get(url):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def sep(char="="):
    print(char * 70)


def print_response(label, data):
    sep("-")
    print("  " + label)
    sep("-")
    fields = [
        ("complaint_id",        data.get("complaint_id")),
        ("category",            data.get("category")),
        ("priority",            data.get("priority")),
        ("ai_confidence",       data.get("ai_confidence")),
        ("assigned_department", data.get("assigned_department")),
        ("status",              data.get("status")),
        ("ai_summary_fallback", data.get("ai_summary_fallback")),
        ("ai_summary",          data.get("ai_summary")),
    ]
    for key, val in fields:
        print(f"  {key:<22} : {val}")


def main():
    # -- 1. Health check -------------------------------------------------------
    sep()
    print("  Health Check")
    sep()
    try:
        health = http_get(f"{BASE_URL}/health")
        print(f"  Status: {health.get('status', 'unknown')}")
    except Exception as e:
        print(f"  ERROR: server not reachable - {e}")
        sys.exit(1)

    # -- 2. POST 3 complaints --------------------------------------------------
    print()
    sep()
    print("  POST /complaints  -  Creating 3 complaints")
    sep()
    created_ids = []

    for item in COMPLAINTS:
        print(f"\n  >> Submitting: {item['label']}  (calling Groq API ...)")
        try:
            resp = http_post(f"{BASE_URL}/complaints", item["payload"])
            created_ids.append(resp["complaint_id"])
            print_response(f"POST Response - {item['label']}", resp)
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"  HTTP {e.code} ERROR: {body}")
        except Exception as e:
            print(f"  ERROR: {e}")
        # small pause between calls to avoid Groq free-tier rate limits
        time.sleep(1)

    # -- 3. GET each complaint by ID -------------------------------------------
    print()
    sep()
    print("  GET /complaints/{id}  -  Confirming persistence")
    sep()

    for i, cid in enumerate(created_ids):
        label = COMPLAINTS[i]["label"]
        try:
            resp = http_get(f"{BASE_URL}/complaints/{cid}")
            print_response(f"GET Response - {label}  [{cid}]", resp)
        except urllib.error.HTTPError as e:
            print(f"  HTTP {e.code} for {cid}: {e.read().decode()}")
        except Exception as e:
            print(f"  ERROR fetching {cid}: {e}")

    print()
    sep()
    print("  End-to-end test complete.")
    sep()
    print()


if __name__ == "__main__":
    main()
