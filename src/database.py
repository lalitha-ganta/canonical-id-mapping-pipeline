
from pathlib import Path
import sqlite3

DB_PATH = Path("data/canonical_mapping.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            run_id TEXT PRIMARY KEY,
            start_time TEXT NOT NULL,
            end_time TEXT,
            status TEXT NOT NULL
                CHECK(status IN ('RUNNING', 'SUCCESS', 'FAILED')),
            input_count INTEGER DEFAULT 0,
            output_count INTEGER DEFAULT 0,
            rejected_count INTEGER DEFAULT 0,
            unresolved_count INTEGER DEFAULT 0,
            error_message TEXT
        );

        CREATE TABLE IF NOT EXISTS source_records (
            record_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            source_file TEXT NOT NULL,
            source_row_number INTEGER NOT NULL,
            source_system TEXT NOT NULL,
            source_id TEXT NOT NULL,
            customer_name TEXT,
            email TEXT,
            event_time TEXT NOT NULL,
            FOREIGN KEY(run_id) REFERENCES pipeline_runs(run_id),
            UNIQUE(run_id, source_file, source_row_number)
        );

        CREATE TABLE IF NOT EXISTS canonical_entities (
            canonical_id TEXT PRIMARY KEY,
            normalized_email TEXT UNIQUE,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS id_mappings (
            source_system TEXT NOT NULL,
            source_id TEXT NOT NULL,
            canonical_id TEXT NOT NULL,
            match_rule TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY(source_system, source_id),
            FOREIGN KEY(canonical_id)
                REFERENCES canonical_entities(canonical_id)
        );

        CREATE TABLE IF NOT EXISTS mapping_history (
            history_id TEXT PRIMARY KEY,
            source_system TEXT NOT NULL,
            source_id TEXT NOT NULL,
            old_canonical_id TEXT,
            new_canonical_id TEXT,
            change_reason TEXT NOT NULL,
            changed_at TEXT NOT NULL,
            run_id TEXT NOT NULL,
            FOREIGN KEY(run_id) REFERENCES pipeline_runs(run_id),
            FOREIGN KEY(old_canonical_id)
                REFERENCES canonical_entities(canonical_id),
            FOREIGN KEY(new_canonical_id)
                REFERENCES canonical_entities(canonical_id)
        );

        CREATE TABLE IF NOT EXISTS mapping_conflicts (
            conflict_id TEXT PRIMARY KEY,
            record_id TEXT NOT NULL,
            candidate_canonical_ids TEXT NOT NULL,
            conflict_reason TEXT NOT NULL,
            run_id TEXT NOT NULL,
            FOREIGN KEY(record_id) REFERENCES source_records(record_id),
            FOREIGN KEY(run_id) REFERENCES pipeline_runs(run_id)
        );

        CREATE TABLE IF NOT EXISTS unresolved_mappings (
            record_id TEXT PRIMARY KEY,
            reason TEXT NOT NULL,
            run_id TEXT NOT NULL,
            FOREIGN KEY(record_id) REFERENCES source_records(record_id),
            FOREIGN KEY(run_id) REFERENCES pipeline_runs(run_id)
        );

        CREATE TABLE IF NOT EXISTS rejected_records (
            reject_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            source_file TEXT NOT NULL,
            source_row_number INTEGER,
            raw_record TEXT,
            reject_reason TEXT NOT NULL,
            FOREIGN KEY(run_id) REFERENCES pipeline_runs(run_id)
        );

        CREATE INDEX IF NOT EXISTS idx_source_email
            ON source_records(email);

        CREATE INDEX IF NOT EXISTS idx_mapping_history_source
            ON mapping_history(source_system, source_id);
        """)

    print("Database tables created successfully!")


if __name__ == "__main__":
    create_tables()
