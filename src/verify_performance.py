
from datetime import datetime
from src.database import get_connection


def verify_performance():
    conn = get_connection()

    try:
        row = conn.execute("""
            SELECT run_id, status, start_time, end_time
            FROM pipeline_runs
            WHERE status = 'SUCCESS'
            ORDER BY rowid DESC
            LIMIT 1
        """).fetchone()

        if row is None:
            print("No successful pipeline run found.")
            return

        run_id, status, start_time, end_time = row

        if not start_time or not end_time:
            print("Run has missing timestamps.")
            return

        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)

        duration = (end - start).total_seconds()

        print("\nPIPELINE PERFORMANCE REPORT")
        print("-" * 40)
        print("Run ID:", run_id)
        print("Status:", status)
        print("Duration (seconds):", round(duration, 4))
        print("Duration (milliseconds):", round(duration * 1000, 2))

    finally:
        conn.close()


if __name__ == "__main__":
    verify_performance()
