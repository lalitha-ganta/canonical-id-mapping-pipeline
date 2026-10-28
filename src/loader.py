
import hashlib
import json
import uuid
from datetime import datetime, timezone

from src.database import get_connection
from src.ingestion import read_customer_data
from src.validation import validate_customers


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def create_record_id(source_file, row_number, row):
    """Generate a stable ID for the same source record."""

    content = json.dumps(
        {
            "source_file": source_file,
            "row_number": row_number,
            "record": row
        },
        sort_keys=True,
        default=str
    )

    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


def load_customers(connection_factory=None):

    source_file = "data/input/customers.csv"
    run_id = str(uuid.uuid4())
    start_time = utc_now()

    # STEP 1: Read source data
    df = read_customer_data()

    if df is None:
        raise FileNotFoundError(source_file)

    # STEP 2: Validate records
    valid, rejected, unresolved = validate_customers(df)

    rejected_rows = (
        set(rejected["row_number"].astype(int).tolist())
        if not rejected.empty
        else set()
    )

    unresolved_rows = {
        int(row["row_number"]): row["reason"]
        for _, row in unresolved.iterrows()
    } if not unresolved.empty else {}

    # STEP 3: Create database connection
    if connection_factory is None:
        connection_factory = get_connection

    conn = connection_factory()

    try:
        # STEP 4: Start database transaction
        with conn:

            conn.execute(
                """
                INSERT INTO pipeline_runs (
                    run_id,
                    start_time,
                    status,
                    input_count,
                    output_count,
                    rejected_count,
                    unresolved_count
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    start_time,
                    "RUNNING",
                    len(df),
                    0,
                    0,
                    0
                )
            )

            inserted = 0

            # STEP 5: Load accepted records
            for _, row in valid.iterrows():

                row_number = int(
                    row["_source_row_number"]
                )

                row_data = row.drop(
                    labels=["_source_row_number"]
                ).to_dict()

                # Convert NaN values to None
                row_data = {
                    key: (
                        None if value != value else value
                    )
                    for key, value in row_data.items()
                }

                if row_number in rejected_rows:
                    continue

                record_id = create_record_id(
                    source_file,
                    row_number,
                    row_data
                )

                cursor = conn.execute(
                    """
                    INSERT OR IGNORE INTO source_records (
                        record_id,
                        run_id,
                        source_file,
                        source_row_number,
                        source_system,
                        source_id,
                        customer_name,
                        email,
                        event_time
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record_id,
                        run_id,
                        source_file,
                        row_number,
                        row_data["source_system"],
                        row_data["source_id"],
                        row_data["customer_name"],
                        row_data["email"],
                        row_data["event_time"]
                    )
                )

                inserted += cursor.rowcount

                # STEP 6: Store unresolved records
                if row_number in unresolved_rows:

                    conn.execute(
                        """
                        INSERT OR IGNORE INTO unresolved_mappings (
                            record_id,
                            reason,
                            run_id
                        )
                        VALUES (?, ?, ?)
                        """,
                        (
                            record_id,
                            unresolved_rows[row_number],
                            run_id
                        )
                    )

            # STEP 7: Store rejected records
            for _, row in rejected.iterrows():

                row_number = int(row["row_number"])

                raw_record = df.iloc[
                    row_number - 2
                ].to_dict()

                reject_id = create_record_id(
                    source_file,
                    row_number,
                    raw_record
                )

                conn.execute(
                    """
                    INSERT OR IGNORE INTO rejected_records (
                        reject_id,
                        run_id,
                        source_file,
                        source_row_number,
                        raw_record,
                        reject_reason
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        reject_id,
                        run_id,
                        source_file,
                        row_number,
                        json.dumps(
                            raw_record,
                            default=str
                        ),
                        row["reason"]
                    )
                )

            # STEP 8: Mark pipeline as successful
            conn.execute(
                """
                UPDATE pipeline_runs
                SET
                    status = 'SUCCESS',
                    end_time = ?,
                    output_count = ?,
                    rejected_count = ?,
                    unresolved_count = ?
                WHERE run_id = ?
                """,
                (
                    utc_now(),
                    inserted,
                    len(rejected),
                    len(unresolved),
                    run_id
                )
            )

        print("\nLOAD COMPLETED SUCCESSFULLY")
        print("Run ID:", run_id)
        print("Inserted source records:", inserted)
        print("Rejected records:", len(rejected))
        print("Unresolved records:", len(unresolved))

    except Exception as error:

        # The transaction above has rolled back.
        # Record the failure in a separate transaction.
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO pipeline_runs (
                        run_id,
                        start_time,
                        end_time,
                        status,
                        input_count,
                        output_count,
                        rejected_count,
                        unresolved_count,
                        error_message
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        start_time,
                        utc_now(),
                        "FAILED",
                        len(df),
                        0,
                        len(rejected),
                        len(unresolved),
                        str(error)
                    )
                )
        except Exception as logging_error:
            print(
                "Failed to record pipeline error:",
                logging_error
            )

        raise

    finally:
        conn.close()


if __name__ == "__main__":
    load_customers()
