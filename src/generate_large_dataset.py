
import csv
import random
from pathlib import Path


def generate_dataset(total_records=100000, seed=42):
    random.seed(seed)

    output_path = Path("data/input/customers_large.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "source_system",
            "source_id",
            "customer_name",
            "email",
            "event_time"
        ])

        for i in range(1, total_records + 1):
            source_system = random.choice(
                ["CRM", "WEBSITE", "APP"]
            )

            writer.writerow([
                source_system,
                f"{source_system}{i:07d}",
                f"Customer {i}",
                f"customer{i}@example.com",
                "2026-10-20T10:00:00Z"
            ])

    print("DATASET GENERATED SUCCESSFULLY")
    print("Total records:", total_records)
    print("File:", output_path)


if __name__ == "__main__":
    generate_dataset()
