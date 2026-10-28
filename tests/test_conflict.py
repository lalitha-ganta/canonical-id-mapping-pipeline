
import hashlib
import uuid
from datetime import datetime, timezone

from src.database import get_connection
from src.matching import process_mappings


def test_conflict_detection():

    conn = get_connection()

    run_id = str(uuid.uuid4())
    record_id = hashlib.sha256(
        b"test_conflict_CRM101_priya"
    ).hexdigest()

    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        with conn:
            conn.execute("""
                INSERT INTO pipeline_runs (
                    run_id, start_time, status, input_count
                )
                VALUES (?, ?, ?, ?)
            """, (
                run_id, timestamp, "RUNNING", 1
            ))

            conn.execute("""
                INSERT OR IGNORE INTO source_records (
                    record_id, run_id, source_file,
                    source_row_number, source_system,
                    source_id, customer_name, email, event_time
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record_id,
                run_id,
                "synthetic_conflict_test.csv",
                2,
                "CRM",
                "CRM101",
                "Priya",
                "priya@gmail.com",
                timestamp
            ))

        # Execute the existing matching engine
        process_mappings()

        conflict = conn.execute("""
            SELECT conflict_reason
            FROM mapping_conflicts
            WHERE record_id = ?
        """, (record_id,)).fetchone()

        assert conflict is not None, \
            "Expected conflict was not detected"

        assert "multiple canonical IDs" in conflict[0]

        print("\nCONFLICT TEST PASSED")
        print("Conflict reason:", conflict[0])

    finally:
        conn.close()


if __name__ == "__main__":
    test_conflict_detection()
