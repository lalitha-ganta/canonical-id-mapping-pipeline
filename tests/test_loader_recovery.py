
import sqlite3
import pytest

from src.loader import load_customers
import src.loader as loader


def test_loader_failure_and_retry(tmp_path, monkeypatch):

    # STEP 1: Create temporary database
    db_path = tmp_path / "test_loader.db"

    conn = sqlite3.connect(db_path)

    conn.executescript("""
        CREATE TABLE pipeline_runs (
            run_id TEXT PRIMARY KEY,
            start_time TEXT,
            end_time TEXT,
            status TEXT,
            input_count INTEGER,
            output_count INTEGER,
            rejected_count INTEGER,
            unresolved_count INTEGER,
            error_message TEXT
        );

        CREATE TABLE source_records (
            record_id TEXT PRIMARY KEY,
            run_id TEXT,
            source_file TEXT,
            source_row_number INTEGER,
            source_system TEXT,
            source_id TEXT,
            customer_name TEXT,
            email TEXT,
            event_time TEXT
        );

        CREATE TABLE unresolved_mappings (
            record_id TEXT PRIMARY KEY,
            reason TEXT,
            run_id TEXT
        );

        CREATE TABLE rejected_records (
            reject_id TEXT PRIMARY KEY,
            run_id TEXT,
            source_file TEXT,
            source_row_number INTEGER,
            raw_record TEXT,
            reject_reason TEXT
        );
    """)

    conn.close()

    # STEP 2: Inject a failure on the first source insert
    class FailingConnection:
        def __init__(self, real_connection):
            self.real_connection = real_connection

        def __enter__(self):
            self.real_connection.__enter__()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return self.real_connection.__exit__(
                exc_type, exc_val, exc_tb
            )

        def execute(self, sql, params=()):
            if "INSERT OR IGNORE INTO source_records" in sql:
                raise RuntimeError("Simulated database failure")

            return self.real_connection.execute(sql, params)

        def close(self):
            self.real_connection.close()

    def failing_factory():
        return FailingConnection(sqlite3.connect(db_path))

    def normal_factory():
        return sqlite3.connect(db_path)

    # STEP 3: Run loader and expect failure
    with pytest.raises(
        RuntimeError,
        match="Simulated database failure"
    ):
        load_customers(connection_factory=failing_factory)

    # STEP 4: Verify rollback and failure logging
    with sqlite3.connect(db_path) as check_conn:
        source_count = check_conn.execute(
            "SELECT COUNT(*) FROM source_records"
        ).fetchone()[0]

        failed_count = check_conn.execute(
            "SELECT COUNT(*) FROM pipeline_runs WHERE status='FAILED'"
        ).fetchone()[0]

    assert source_count == 0
    assert failed_count == 1

    # STEP 5: Retry with normal connection
    load_customers(connection_factory=normal_factory)

    with sqlite3.connect(db_path) as check_conn:
        source_count_after_retry = check_conn.execute(
            "SELECT COUNT(*) FROM source_records"
        ).fetchone()[0]

        success_count = check_conn.execute(
            "SELECT COUNT(*) FROM pipeline_runs WHERE status='SUCCESS'"
        ).fetchone()[0]

    assert source_count_after_retry == 7
    assert success_count == 1

    # STEP 6: Rerun to verify idempotency
    load_customers(connection_factory=normal_factory)

    with sqlite3.connect(db_path) as check_conn:
        final_count = check_conn.execute(
            "SELECT COUNT(*) FROM source_records"
        ).fetchone()[0]

    assert final_count == 7
