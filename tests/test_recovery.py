
import sqlite3
import pytest


def test_transaction_rollback(tmp_path):

    # Create a temporary database for testing
    db_path = tmp_path / "recovery_test.db"

    conn = sqlite3.connect(db_path)

    try:
        conn.execute("""
            CREATE TABLE customers (
                customer_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL
            )
        """)

        # Simulate a pipeline failure
        with pytest.raises(RuntimeError):

            with conn:
                conn.execute("""
                    INSERT INTO customers
                    VALUES (?, ?)
                """, ("CRM101", "Rahul"))

                # Simulate failure after first insert
                raise RuntimeError(
                    "Simulated pipeline failure"
                )

        # Check whether the insert was rolled back
        count = conn.execute("""
            SELECT COUNT(*) FROM customers
        """).fetchone()[0]

        assert count == 0

    finally:
        conn.close()
