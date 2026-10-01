import sqlite3
import json
from pathlib import Path


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "decision_guardian.db"


# ============================================================
# CONNECTION
# ============================================================

def get_connection():
    connection = sqlite3.connect(str(DB_PATH))

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS incidents (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            incident_id TEXT UNIQUE NOT NULL,

            timestamp TEXT NOT NULL,

            language TEXT,

            risk_score INTEGER,

            risk_level TEXT,

            decision_transition TEXT,

            events TEXT,

            timeline TEXT,

            dangerous_transitions TEXT,

            iocs TEXT,

            mitre TEXT,

            recommendations TEXT,

            intervention TEXT

        )
    """)

    connection.commit()

    connection.close()


# ============================================================
# SAVE INCIDENT
# ============================================================

def save_incident(result):

    connection = get_connection()

    connection.execute("""
        INSERT OR REPLACE INTO incidents (

            incident_id,

            timestamp,

            language,

            risk_score,

            risk_level,

            decision_transition,

            events,

            timeline,

            dangerous_transitions,

            iocs,

            mitre,

            recommendations,

            intervention

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        result.get("incident_id"),

        result.get("timestamp"),

        result.get("language"),

        result.get("risk_score"),

        result.get("risk_level"),

        result.get("decision_transition"),

        json.dumps(
            result.get("events", []),
            ensure_ascii=False
        ),

        json.dumps(
            result.get("timeline", []),
            ensure_ascii=False
        ),

        json.dumps(
            result.get("dangerous_transitions", []),
            ensure_ascii=False
        ),

        json.dumps(
            result.get("iocs", {}),
            ensure_ascii=False
        ),

        json.dumps(
            result.get("mitre", []),
            ensure_ascii=False
        ),

        json.dumps(
            result.get("recommendations", []),
            ensure_ascii=False
        ),

        result.get("intervention")

    ))

    connection.commit()

    connection.close()


# ============================================================
# GET INCIDENTS
# ============================================================

def get_incidents(limit=50):

    connection = get_connection()

    rows = connection.execute("""
        SELECT
            id,
            incident_id,
            timestamp,
            language,
            risk_score,
            risk_level,
            decision_transition,
            events,
            timeline,
            dangerous_transitions,
            iocs,
            mitre,
            recommendations,
            intervention

        FROM incidents

        ORDER BY id DESC

        LIMIT ?
    """, (limit,)).fetchall()

    connection.close()

    return [dict(row) for row in rows]


# ============================================================
# STATISTICS
# ============================================================

def get_statistics():

    connection = get_connection()

    total = connection.execute("""
        SELECT COUNT(*)
        FROM incidents
    """).fetchone()[0]

    high = connection.execute("""
        SELECT COUNT(*)
        FROM incidents
        WHERE risk_level IN ('high', 'critical')
    """).fetchone()[0]

    medium = connection.execute("""
        SELECT COUNT(*)
        FROM incidents
        WHERE risk_level = 'medium'
    """).fetchone()[0]

    low = connection.execute("""
        SELECT COUNT(*)
        FROM incidents
        WHERE risk_level IN ('low', 'normal')
    """).fetchone()[0]

    connection.close()

    return {
        "total": total,
        "high": high,
        "medium": medium,
        "low": low
    }