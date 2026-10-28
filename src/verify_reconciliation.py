
from src.ingestion import read_customer_data
from src.validation import validate_customers
from src.database import get_connection


# STEP 1: Verify CSV input reconciliation
def verify_reconciliation():

    df = read_customer_data()

    if df is None:
        raise ValueError("Unable to read input data")

    valid, rejected, unresolved = validate_customers(df)

    input_count = len(df)
    accepted_count = len(valid)
    rejected_count = len(rejected)
    unresolved_count = len(unresolved)

    matchable_count = accepted_count - unresolved_count

    print("\nDATA RECONCILIATION REPORT")
    print("-" * 45)

    print("Total input records:", input_count)
    print("Accepted records:", accepted_count)
    print("Rejected records:", rejected_count)
    print("Unresolved records:", unresolved_count)
    print("Matchable records:", matchable_count)

    # Check that all input records are accounted for
    assert input_count == accepted_count + rejected_count, (
        "Input reconciliation failed"
    )

    # Unresolved records are part of accepted records
    assert 0 <= unresolved_count <= accepted_count

    print("\nCSV RECONCILIATION PASSED")


# STEP 2: Verify SQLite database record counts
def verify_database_reconciliation():

    conn = get_connection()

    try:
        tables = [
            "source_records",
            "id_mappings",
            "mapping_history",
            "mapping_conflicts",
            "unresolved_mappings",
            "rejected_records"
        ]

        print("\nDATABASE RECONCILIATION REPORT")
        print("-" * 45)

        for table in tables:
            count = conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            print(f"{table}: {count}")

        print("\nDATABASE COUNTS DISPLAYED SUCCESSFULLY")

    finally:
        conn.close()


# STEP 3: Execute both verification functions
if __name__ == "__main__":

    verify_reconciliation()

    verify_database_reconciliation()
