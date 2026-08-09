"""
DatabaseManager
---------------
Handles all SQLite operations for the AI Smart Civic Services platform.
Single responsibility: persistence layer only. No AI logic, no business rules —
those live in ComplaintManager / AIAnalyzer.
"""

import sqlite3
from contextlib import contextmanager
from typing import Optional
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_path: str = "civic.db"):
        self.db_path = db_path
        self._init_schema()

    @contextmanager
    def _get_connection(self):
        """Yields a connection with row access by column name, closes safely."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS complaints (
                    complaint_id TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    category TEXT,
                    priority TEXT,
                    location TEXT,
                    date TEXT,
                    status TEXT DEFAULT 'Open',
                    assigned_department TEXT,
                    ai_summary TEXT,
                    ai_confidence REAL,
                    resolved_at TIMESTAMP,
                    submitted_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS departments (
                    department_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category_handled TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('citizen', 'admin')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Migration check: add submitted_by if missing in existing database
            cols = [r["name"] for r in conn.execute("PRAGMA table_info(complaints)").fetchall()]
            if "submitted_by" not in cols:
                conn.execute("ALTER TABLE complaints ADD COLUMN submitted_by TEXT")

            # Indexes for the filter/search endpoints
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON complaints(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_priority ON complaints(priority)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON complaints(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_submitted_by ON complaints(submitted_by)")

            # Auto-seed default departments if table is empty
            count = conn.execute("SELECT COUNT(*) FROM departments").fetchone()[0]
            if count == 0:
                defaults = [
                    ("DEPT-ROAD", "Roads Department", "Road"),
                    ("DEPT-WATER", "Water Board", "Water/Drainage"),
                    ("DEPT-WASTE", "Sanitation Department", "Waste"),
                    ("DEPT-ELEC", "Power Department", "Electricity"),
                    ("DEPT-SAFE", "Public Safety Department", "Safety"),
                    ("DEPT-GEN", "General Services Department", "Other"),
                ]
                conn.executemany(
                    "INSERT INTO departments (department_id, name, category_handled) VALUES (?, ?, ?)",
                    defaults
                )

    # ---------- USERS ----------
    def create_user(self, user_dict: dict) -> bool:
        """
        user_dict: user_id, name, email, password_hash, role
        """
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO users (user_id, name, email, password_hash, role)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    user_dict["user_id"],
                    user_dict["name"],
                    user_dict["email"].lower().strip(),
                    user_dict["password_hash"],
                    user_dict["role"]
                ))
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user_by_email(self, email: str) -> Optional[dict]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE LOWER(email) = ?", (email.lower().strip(),)
            ).fetchone()
            return dict(row) if row else None

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
            return dict(row) if row else None

    # ---------- CREATE ----------
    def insert_complaint(self, complaint: dict) -> bool:
        """
        complaint dict expected keys:
        complaint_id, description, category, priority, location, date,
        status, assigned_department, ai_summary, ai_confidence, submitted_by
        """
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO complaints (
                        complaint_id, description, category, priority,
                        location, date, status, assigned_department,
                        ai_summary, ai_confidence, submitted_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    complaint["complaint_id"],
                    complaint["description"],
                    complaint.get("category"),
                    complaint.get("priority"),
                    complaint.get("location"),
                    complaint.get("date", datetime.utcnow().isoformat()),
                    complaint.get("status", "Open"),
                    complaint.get("assigned_department"),
                    complaint.get("ai_summary"),
                    complaint.get("ai_confidence"),
                    complaint.get("submitted_by"),
                ))
            return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error:
            return False


    # ---------- READ ----------
    def get_complaint(self, complaint_id: str) -> Optional[dict]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM complaints WHERE complaint_id = ?", (complaint_id,)
            ).fetchone()
            return dict(row) if row else None

    def list_complaints(self, filters: Optional[dict] = None) -> list[dict]:
        """
        filters supports any combination of: category, priority, status,
        location, department (assigned_department), date_from, date_to.
        Unknown/invalid filter keys are silently ignored (per error-handling
        requirement — don't 500 on a bad query param).
        """
        filters = filters or {}
        allowed = {
            "category": "category = ?",
            "priority": "priority = ?",
            "status": "status = ?",
            "location": "location = ?",
            "department": "assigned_department = ?",
        }

        clauses = []
        params = []
        for key, clause in allowed.items():
            if filters.get(key):
                clauses.append(clause)
                params.append(filters[key])

        if filters.get("date_from"):
            clauses.append("date >= ?")
            params.append(filters["date_from"])
        if filters.get("date_to"):
            clauses.append("date <= ?")
            params.append(filters["date_to"])

        query = "SELECT * FROM complaints"
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY created_at DESC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def list_complaints_by_user(self, user_id: str) -> list[dict]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM complaints WHERE submitted_by = ? ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    # ---------- UPDATE ----------

    def update_status(self, complaint_id: str, status: str) -> bool:
        valid_statuses = {"Open", "Assigned", "In Progress", "Resolved"}
        if status not in valid_statuses:
            return False

        resolved_at = datetime.utcnow().isoformat() if status == "Resolved" else None

        with self._get_connection() as conn:
            cursor = conn.execute(
                """UPDATE complaints
                   SET status = ?, resolved_at = COALESCE(?, resolved_at)
                   WHERE complaint_id = ?""",
                (status, resolved_at, complaint_id),
            )
            return cursor.rowcount > 0

    def assign_department(self, complaint_id: str, department: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE complaints SET assigned_department = ? WHERE complaint_id = ?",
                (department, complaint_id),
            )
            return cursor.rowcount > 0

    # ---------- ANALYTICS SUPPORT ----------
    def get_all_for_stats(self) -> list[dict]:
        """Raw rows for StatsService to compute distributions/variance/etc on."""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM complaints").fetchall()
            return [dict(r) for r in rows]

    # ---------- DEPARTMENTS ----------
    def seed_departments(self, departments: list[dict]):
        """departments: [{department_id, name, category_handled}, ...]"""
        with self._get_connection() as conn:
            for d in departments:
                conn.execute("""
                    INSERT OR IGNORE INTO departments (department_id, name, category_handled)
                    VALUES (?, ?, ?)
                """, (d["department_id"], d["name"], d["category_handled"]))

    def get_department_for_category(self, category: str) -> Optional[str]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT name FROM departments WHERE category_handled = ? LIMIT 1",
                (category,),
            ).fetchone()
            return row["name"] if row else None
