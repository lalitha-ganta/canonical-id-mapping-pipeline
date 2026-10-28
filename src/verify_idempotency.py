
from src.database import get_connection


def verify_idempotency():
    conn = get_connection()

    tables = [
        "source_records",
        "id_mappings",
        "mapping_history",
        "mapping_conflicts",
        "unresolved_mappings",
        "rejected_records"
    ]

    print("\nDATABASE RECORD COUNTS")
    print("-" * 40)

    try:
        for table in tables:
            count = conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            print(f"{table}: {count}")

    finally:
        conn.close()


if __name__ == "__main__":
    verify_idempotency()
