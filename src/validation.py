
import pandas as pd
import re

REQUIRED_COLUMNS = [
    "source_system",
    "source_id",
    "customer_name",
    "email",
    "event_time"
]


def validate_customers(df):

    valid_records = []
    rejected_records = []
    unresolved_records = []

    seen_events = set()

    # Validate input schema
    if list(df.columns) != REQUIRED_COLUMNS:
        raise ValueError(
            f"Invalid CSV schema. Expected: {REQUIRED_COLUMNS}"
        )

    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    for index, row in df.iterrows():

        row_number = index + 2

        source_system = row["source_system"]
        source_id = row["source_id"]
        email = row["email"]
        event_time = row["event_time"]

        # Rule 1: Check missing or blank identifiers
        if (
            pd.isna(source_system)
            or pd.isna(source_id)
            or not str(source_system).strip()
            or not str(source_id).strip()
        ):
            rejected_records.append({
                "row_number": row_number,
                "reason": "Missing or blank source identifier"
            })
            continue

        # Normalize source identifiers
        source_system = str(source_system).strip().upper()
        source_id = str(source_id).strip()

        # Rule 2: Detect duplicate events
        event_key = (
            source_system,
            source_id,
            str(event_time)
        )

        if event_key in seen_events:
            rejected_records.append({
                "row_number": row_number,
                "reason": "Duplicate source event"
            })
            continue

        seen_events.add(event_key)

        # Rule 3: Missing email is unresolved
        if pd.isna(email) or not str(email).strip():
            unresolved_records.append({
             "row_number": row_number,
             "source_id": source_id,
             "reason": "Missing email"
    })

            valid_row = row.to_dict()
            valid_row["_source_row_number"] = row_number
            valid_row["source_system"] = source_system
            valid_row["source_id"] = source_id

            valid_records.append(valid_row)
            continue

        # Rule 4: Validate email format
        normalized_email = str(email).strip().lower()

        if not re.fullmatch(email_pattern, normalized_email):
            rejected_records.append({
                "row_number": row_number,
                "reason": "Invalid email format"
            })
            continue

        # Rule 5: Accept valid record
        valid_row = row.to_dict()
        valid_row["_source_row_number"] = row_number
        valid_row["source_system"] = source_system
        valid_row["source_id"] = source_id
        

        valid_records.append(valid_row)

    
    return (
    pd.DataFrame(
        valid_records,
        columns=REQUIRED_COLUMNS + ["_source_row_number"]
    ),
    pd.DataFrame(rejected_records),
    pd.DataFrame(unresolved_records)
)



if __name__ == "__main__":

    from src.ingestion import read_customer_data

    df = read_customer_data()

    if df is not None:
        valid, rejected, unresolved = validate_customers(df)

        print("\nVALID RECORDS:", len(valid))
        print("REJECTED RECORDS:", len(rejected))
        print("UNRESOLVED RECORDS:", len(unresolved))

        print("\nRejected details:")
        print(rejected.to_string(index=False))

        print("\nUnresolved details:")
        print(unresolved.to_string(index=False))
