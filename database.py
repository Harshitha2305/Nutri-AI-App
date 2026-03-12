# =============================================================================
# database.py — NutriAI v4
# SQLite database layer: schema creation, connection pool, all CRUD helpers.
#
# Tables
# ──────
#   users          — account credentials + display info
#   user_profiles  — physical/dietary profile linked to a user
#   meal_history   — one row per generated daily plan (for history view)
#   chat_sessions  — persisted chat messages per user
#
# Usage
#   from database import Database
#   db = Database()                          # auto-creates nutri_ai.db
#   uid = db.create_user("Alice","a@b.com","hash")
#   db.save_profile(uid, {...})
# =============================================================================

import sqlite3
import os
from datetime import datetime
from typing import Optional

DB_PATH = os.environ.get("NUTRI_AI_DB", "nutri_ai.db")


class Database:
    """Thin wrapper around a SQLite connection with auto-schema migration."""

    def __init__(self, path: str = DB_PATH):
        self.path = path
        # Persistent connection so :memory: works across all calls
        self._connection = sqlite3.connect(path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._init_schema()

    # ── Connection helper ─────────────────────────────────────────────────────

    def _conn(self) -> sqlite3.Connection:
        """Return the persistent connection (works for both file and :memory:)."""
        return self._connection

    # ── Schema ────────────────────────────────────────────────────────────────

    def _init_schema(self):
        ddl = """
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now')),
            last_login    TEXT
        );

        CREATE TABLE IF NOT EXISTS user_profiles (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            age            INTEGER,
            gender         TEXT,
            height_cm      REAL,
            weight_kg      REAL,
            activity_level TEXT,
            fitness_goal   TEXT,
            diet_preference TEXT,
            allergies      TEXT,   -- comma-separated string
            cuisine_pref   TEXT    DEFAULT 'both',
            updated_at     TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS meal_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            plan_date   TEXT    NOT NULL,       -- 'YYYY-MM-DD'
            plan_type   TEXT    DEFAULT 'daily',
            plan_json   TEXT    NOT NULL,       -- JSON blob of the full plan dict
            calories    INTEGER,
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS chat_sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role        TEXT    NOT NULL,       -- 'user' | 'assistant'
            content     TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now'))
        );
        """
        with self._conn() as conn:
            conn.executescript(ddl)

    # ═════════════════════════════════════════════════════════════════════════
    # USER CRUD
    # ═════════════════════════════════════════════════════════════════════════

    def create_user(self, name: str, email: str, password_hash: str) -> Optional[int]:
        """
        Insert a new user row.
        Returns new user id, or None if email already exists.
        """
        try:
            with self._conn() as conn:
                cur = conn.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name.strip(), email.strip().lower(), password_hash),
                )
                return cur.lastrowid
        except sqlite3.IntegrityError:
            return None   # duplicate email

    def get_user_by_email(self, email: str) -> Optional[sqlite3.Row]:
        """Fetch full user row by email (case-insensitive). Returns None if not found."""
        with self._conn() as conn:
            return conn.execute(
                "SELECT * FROM users WHERE email = ? COLLATE NOCASE",
                (email.strip(),)
            ).fetchone()

    def get_user_by_id(self, user_id: int) -> Optional[sqlite3.Row]:
        with self._conn() as conn:
            return conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()

    def update_last_login(self, user_id: int):
        with self._conn() as conn:
            conn.execute(
                "UPDATE users SET last_login = datetime('now') WHERE id = ?",
                (user_id,)
            )

    def update_user_name(self, user_id: int, name: str):
        with self._conn() as conn:
            conn.execute(
                "UPDATE users SET name = ? WHERE id = ?", (name, user_id)
            )

    def update_password(self, user_id: int, new_hash: str):
        with self._conn() as conn:
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (new_hash, user_id)
            )

    def delete_user(self, user_id: int):
        with self._conn() as conn:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))

    # ═════════════════════════════════════════════════════════════════════════
    # USER PROFILE CRUD
    # ═════════════════════════════════════════════════════════════════════════

    def save_profile(self, user_id: int, data: dict):
        """
        Upsert the user_profile row for user_id.
        data keys: age, gender, height_cm, weight_kg, activity_level,
                   fitness_goal, diet_preference, allergies (list|str), cuisine_pref
        """
        allergies = data.get("allergies", "")
        if isinstance(allergies, list):
            allergies = ", ".join(allergies)

        with self._conn() as conn:
            conn.execute("""
                INSERT INTO user_profiles
                    (user_id, age, gender, height_cm, weight_kg,
                     activity_level, fitness_goal, diet_preference,
                     allergies, cuisine_pref, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ON CONFLICT(user_id) DO UPDATE SET
                    age            = excluded.age,
                    gender         = excluded.gender,
                    height_cm      = excluded.height_cm,
                    weight_kg      = excluded.weight_kg,
                    activity_level = excluded.activity_level,
                    fitness_goal   = excluded.fitness_goal,
                    diet_preference= excluded.diet_preference,
                    allergies      = excluded.allergies,
                    cuisine_pref   = excluded.cuisine_pref,
                    updated_at     = excluded.updated_at
            """, (
                user_id,
                data.get("age"),
                data.get("gender"),
                data.get("height_cm"),
                data.get("weight_kg"),
                data.get("activity_level"),
                data.get("fitness_goal"),
                data.get("diet_preference"),
                allergies,
                data.get("cuisine_pref", "both"),
            ))

    def get_profile(self, user_id: int) -> Optional[dict]:
        """
        Returns profile as a plain dict (or None if not set up yet).
        Allergies are returned as a list[str].
        """
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM user_profiles WHERE user_id = ?", (user_id,)
            ).fetchone()

        if not row:
            return None

        d = dict(row)
        raw_allergies = d.get("allergies") or ""
        d["allergies"] = [a.strip() for a in raw_allergies.split(",") if a.strip()]
        return d

    def profile_complete(self, user_id: int) -> bool:
        """Returns True if the user has filled in all required profile fields."""
        p = self.get_profile(user_id)
        if not p:
            return False
        required = ["age", "gender", "height_cm", "weight_kg",
                    "activity_level", "fitness_goal", "diet_preference"]
        return all(p.get(k) for k in required)

    # ═════════════════════════════════════════════════════════════════════════
    # MEAL HISTORY
    # ═════════════════════════════════════════════════════════════════════════

    def save_meal_plan(self, user_id: int, plan_dict: dict,
                       plan_type: str = "daily") -> int:
        """Persist a generated meal plan. Returns new row id."""
        import json
        today = datetime.now().strftime("%Y-%m-%d")
        cal   = plan_dict.get("daily_totals", {}).get("calories", 0)
        with self._conn() as conn:
            cur = conn.execute("""
                INSERT INTO meal_history (user_id, plan_date, plan_type, plan_json, calories)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, today, plan_type, json.dumps(plan_dict), cal))
            return cur.lastrowid

    def get_recent_plans(self, user_id: int, limit: int = 7) -> list:
        """Returns last `limit` daily plans as list of dicts."""
        import json
        with self._conn() as conn:
            rows = conn.execute("""
                SELECT plan_date, plan_type, plan_json, calories, created_at
                FROM meal_history
                WHERE user_id = ? AND plan_type = 'daily'
                ORDER BY created_at DESC LIMIT ?
            """, (user_id, limit)).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            try:
                d["plan"] = json.loads(d["plan_json"])
            except Exception:
                d["plan"] = {}
            result.append(d)
        return result

    # ═════════════════════════════════════════════════════════════════════════
    # CHAT SESSION
    # ═════════════════════════════════════════════════════════════════════════

    def save_chat_message(self, user_id: int, role: str, content: str):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO chat_sessions (user_id, role, content) VALUES (?, ?, ?)",
                (user_id, role, content),
            )

    def get_chat_history(self, user_id: int, limit: int = 40) -> list[dict]:
        """Returns last `limit` messages as [{"role":…, "content":…}, …]."""
        with self._conn() as conn:
            rows = conn.execute("""
                SELECT role, content FROM chat_sessions
                WHERE user_id = ?
                ORDER BY created_at DESC LIMIT ?
            """, (user_id, limit)).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

    def clear_chat_history(self, user_id: int):
        with self._conn() as conn:
            conn.execute("DELETE FROM chat_sessions WHERE user_id = ?", (user_id,))

    # ═════════════════════════════════════════════════════════════════════════
    # STATS (for profile dashboard)
    # ═════════════════════════════════════════════════════════════════════════

    def user_stats(self, user_id: int) -> dict:
        """Quick aggregate stats for the user dashboard."""
        with self._conn() as conn:
            plans  = conn.execute(
                "SELECT COUNT(*) FROM meal_history WHERE user_id = ?", (user_id,)
            ).fetchone()[0]
            chats  = conn.execute(
                "SELECT COUNT(*) FROM chat_sessions WHERE user_id = ? AND role='user'",
                (user_id,)
            ).fetchone()[0]
            joined = conn.execute(
                "SELECT created_at FROM users WHERE id = ?", (user_id,)
            ).fetchone()
        return {
            "plans_generated": plans,
            "chat_messages":   chats,
            "member_since":    joined[0][:10] if joined else "–",
        }
