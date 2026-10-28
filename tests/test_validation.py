
import pandas as pd

from src.validation import validate_customers


COLUMNS = [
    "source_system",
    "source_id",
    "customer_name",
    "email",
    "event_time"
]


def make_dataframe(rows):
    return pd.DataFrame(rows, columns=COLUMNS)


def test_valid_customer():
    df = make_dataframe([
        ["CRM", "CRM101", "Rahul",
         "rahul@gmail.com", "2026-10-20T10:00:00Z"]
    ])

    valid, rejected, unresolved = validate_customers(df)

    assert len(valid) == 1
    assert len(rejected) == 0
    assert len(unresolved) == 0


def test_missing_email():
    df = make_dataframe([
        ["CRM", "CRM102", "Priya",
         None, "2026-10-20T10:00:00Z"]
    ])

    valid, rejected, unresolved = validate_customers(df)

    assert len(valid) == 1
    assert len(rejected) == 0
    assert len(unresolved) == 1


def test_invalid_email():
    df = make_dataframe([
        ["CRM", "CRM103", "Amit",
         "invalid-email", "2026-10-20T10:00:00Z"]
    ])

    valid, rejected, unresolved = validate_customers(df)

    assert len(valid) == 0
    assert len(rejected) == 1
    assert len(unresolved) == 0


def test_missing_source_id():
    df = make_dataframe([
        ["CRM", None, "Rahul",
         "rahul@gmail.com", "2026-10-20T10:00:00Z"]
    ])

    valid, rejected, unresolved = validate_customers(df)

    assert len(valid) == 0
    assert len(rejected) == 1


def test_empty_batch():
    df = make_dataframe([])

    valid, rejected, unresolved = validate_customers(df)

    assert len(valid) == 0
    assert len(rejected) == 0
    assert len(unresolved) == 0

def test_duplicate_source_record():
    df = make_dataframe([
        ["CRM", "CRM101", "Rahul",
         "rahul@gmail.com", "2026-10-20T10:00:00Z"],
        ["CRM", "CRM101", "Rahul",
         "rahul@gmail.com", "2026-10-20T10:00:00Z"]
    ])

    valid, rejected, unresolved = validate_customers(df)

    # Current validator does not yet detect duplicates.
    # This test describes the behavior we want.
    assert len(valid) == 1
    assert len(rejected) == 1


def test_unexpected_schema():
    df = pd.DataFrame([
        {
            "source_system": "CRM",
            "source_id": "CRM101",
            "customer_name": "Rahul",
            "email": "rahul@gmail.com",
            "unexpected_column": "extra"
        }
    ])

    import pytest

    with pytest.raises(ValueError):
        validate_customers(df)


def test_blank_source_id():
    df = make_dataframe([
        ["CRM", "   ", "Rahul",
         "rahul@gmail.com", "2026-10-20T10:00:00Z"]
    ])

    valid, rejected, unresolved = validate_customers(df)

    # Whitespace-only identifiers should be rejected.
    assert len(valid) == 0
    assert len(rejected) == 1
