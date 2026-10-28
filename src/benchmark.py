
import time
from pathlib import Path

import pandas as pd

from src.validation import validate_customers


def run_benchmark():
    file_path = Path("data/input/customers_large.csv")

    if not file_path.exists():
        print("ERROR: Large dataset not found.")
        return

    print("\nPERFORMANCE BENCHMARK")
    print("-" * 45)

    start_time = time.perf_counter()

    df = pd.read_csv(file_path)

    ingestion_time = time.perf_counter() - start_time

    validation_start = time.perf_counter()

    valid, rejected, unresolved = validate_customers(df)

    validation_time = time.perf_counter() - validation_start

    total_time = time.perf_counter() - start_time

    total_records = len(df)

    print("Total input records:", total_records)
    print("Valid records:", len(valid))
    print("Rejected records:", len(rejected))
    print("Unresolved records:", len(unresolved))

    assert total_records == len(valid) + len(rejected), (
        "Reconciliation failed"
    )

    print("\nPERFORMANCE RESULTS")
    print("-" * 45)
    print(f"CSV reading time: {ingestion_time:.3f} seconds")
    print(f"Validation time: {validation_time:.3f} seconds")
    print(f"Total processing time: {total_time:.3f} seconds")

    if total_time > 0:
        throughput = total_records / total_time
        print(f"Throughput: {throughput:.2f} records/second")

    print("\nRECONCILIATION PASSED")
    print("BENCHMARK COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    run_benchmark()
