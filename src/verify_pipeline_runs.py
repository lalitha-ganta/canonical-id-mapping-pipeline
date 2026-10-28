
from src.database import get_connection


def verify_pipeline_runs():
    conn = get_connection()

    try:
        cursor = conn.execute("""
            SELECT *
            FROM pipeline_runs
            ORDER BY rowid DESC
            LIMIT 3
        """)

        print("\nPIPELINE RUN HISTORY")
        print("-" * 60)

        columns = [item[0] for item in cursor.description]

        for row in cursor.fetchall():
            print("\nRUN:")
            for column, value in zip(columns, row):
                print(f"  {column}: {value}")

    finally:
        conn.close()


if __name__ == "__main__":
    verify_pipeline_runs()
