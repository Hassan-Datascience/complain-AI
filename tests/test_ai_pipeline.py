import os
import unittest
import tempfile
from fastapi.testclient import TestClient

from app.main import app
from app.services.database_manager import DatabaseManager
from app.services.ai_analyzer import AIAnalyzer
from app.services.complaint_manager import ComplaintManager
from app.services.stats_service import StatsService

class TestCivicServices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db_file = "test_civic.db"
        cls.db = DatabaseManager(db_path=cls.db_file)
        cls.ai = AIAnalyzer()
        cls.manager = ComplaintManager(db_manager=cls.db, ai_analyzer=cls.ai)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.db_file):
            try:
                os.remove(cls.db_file)
            except Exception:
                pass

    def test_01_database_manager(self):
        """Tests DatabaseManager schema initialization and basic CRUD."""
        complaint = {
            "complaint_id": "CMP-TEST001",
            "description": "Deep pothole on Main Street near 5th Avenue.",
            "category": "Road",
            "priority": "Medium",
            "location": "Main Street",
            "status": "Open",
            "assigned_department": "Roads Department",
            "ai_summary": "Pothole on Main Street needs repair.",
            "ai_confidence": 0.95
        }
        inserted = self.db.insert_complaint(complaint)
        self.assertTrue(inserted)

        fetched = self.db.get_complaint("CMP-TEST001")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["category"], "Road")

        # Status update
        updated = self.db.update_status("CMP-TEST001", "Resolved")
        self.assertTrue(updated)
        fetched_after = self.db.get_complaint("CMP-TEST001")
        self.assertEqual(fetched_after["status"], "Resolved")
        self.assertIsNotNone(fetched_after["resolved_at"])

    def test_02_ai_analyzer(self):
        """Tests AIAnalyzer classification and priority prediction."""
        res_cat, conf_cat = self.ai.classify("Main water pipeline burst flooding the street with brown water.")
        self.assertEqual(res_cat, "Water/Drainage")
        self.assertGreater(conf_cat, 0.5)

        res_prio, conf_prio = self.ai.predict_priority("High voltage live electric wire hanging down on sidewalk.")
        self.assertIn(res_prio, ["Critical", "High"])

    def test_03_stats_service(self):
        """Tests StatsService metrics calculations."""
        raw_rows = [
            {"category": "Road", "priority": "Medium", "status": "Resolved", "created_at": "2026-08-01T10:00:00", "resolved_at": "2026-08-01T14:00:00"},
            {"category": "Water/Drainage", "priority": "Critical", "status": "Resolved", "created_at": "2026-08-01T10:00:00", "resolved_at": "2026-08-01T20:00:00"},
            {"category": "Waste", "priority": "Low", "status": "Open", "created_at": "2026-08-02T10:00:00"},
        ]
        stats = StatsService(raw_rows)
        res_stats = stats.get_resolution_stats()
        self.assertEqual(res_stats["total_resolved"], 2)
        self.assertEqual(res_stats["mean_hours"], 7.0) # (4 + 10) / 2
        self.assertIn("average resolution time is 7.0 hours", res_stats["interpretation"])

    def test_04_fastapi_endpoints(self):
        """Tests FastAPI REST API routes."""
        # 1. Health check
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)

        # 2. Create complaint via API
        payload = {
            "description": "Garbage dump bin overflowing and foul smell near public park.",
            "location": "Sector 4 Park"
        }
        res_post = self.client.post("/complaints", json=payload)
        self.assertEqual(res_post.status_code, 201)
        data = res_post.json()
        self.assertEqual(data["category"], "Waste")
        self.assertEqual(data["assigned_department"], "Sanitation Department")
        complaint_id = data["complaint_id"]

        # 3. GET complaint by ID
        res_get = self.client.get(f"/complaints/{complaint_id}")
        self.assertEqual(res_get.status_code, 200)

        # 4. PATCH status
        res_patch = self.client.patch(f"/complaints/{complaint_id}/status", json={"status": "In Progress"})
        self.assertEqual(res_patch.status_code, 200)
        self.assertEqual(res_patch.json()["status"], "In Progress")

        # 5. GET analytics summary
        res_summary = self.client.get("/analytics/summary")
        self.assertEqual(res_summary.status_code, 200)
        self.assertGreater(res_summary.json()["total_complaints"], 0)

        # 6. GET analytics stats
        res_stats = self.client.get("/analytics/stats")
        self.assertEqual(res_stats.status_code, 200)

        # 7. GET analytics trends
        res_trends = self.client.get("/analytics/trends")
        self.assertEqual(res_trends.status_code, 200)

    def test_05_ai_evaluation_suite(self):
        """Runs 10 realistic test complaints and prints AI performance evidence table."""
        test_cases = [
            "Massive pothole on Expressway causing tire punctures and traffic jams.",
            "Contaminated tap water running dark brown in Sector 9 apartments.",
            "Community dumpster overflowing with rotting garbage attracting pests.",
            "Live electrical cable snapped and lying across entrance to school.",
            "Stray dog pack acting aggressively near kindergarten playground.",
            "Public park fountain turned off and lawn overgrown with weeds.",
            "Broken sewer line leaking raw sewage into street gutter.",
            "Streetlights out on Elm Street for 4 consecutive nights.",
            "Derelict abandoned car left blocking fire hydrant.",
            "Loud commercial music played until 3 AM in residential zone."
        ]

        print("\n" + "=" * 90)
        print("                      AI TESTING EVALUATION RESULTS TABLE")
        print("=" * 90)
        print(f"{'Input Snippet':<40} | {'Category':<15} | {'Priority':<10} | {'Confidence':<10}")
        print("-" * 90)

        for text in test_cases:
            analysis = self.ai.analyze(text)
            snippet = text[:38] + ".." if len(text) > 38 else text
            cat = analysis["category"]
            prio = analysis["priority"]
            conf = analysis["ai_confidence"]
            print(f"{snippet:<40} | {cat:<15} | {prio:<10} | {conf:<10.2f}")
        print("=" * 90 + "\n")

if __name__ == "__main__":
    unittest.main()
