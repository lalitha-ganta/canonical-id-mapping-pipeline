
from src.database import get_connection


def verify_mapping_history():
    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                source_system,
                source_id,
                old_canonical_id,
                new_canonical_id,
                change_reason
            FROM mapping_history
            ORDER BY source_system, source_id
        """).fetchall()

        print("\nMAPPING HISTORY REPORT")
        print("-" * 75)

        for row in rows:
            print(
                "Source:", row[0],
                "| ID:", row[1],
                "| Old:", row[2],
                "| New:", row[3],
                "| Reason:", row[4]
            )

        print("\nTotal history records:", len(rows))

    finally:
        conn.close()


if __name__ == "__main__":
    verify_mapping_history()
