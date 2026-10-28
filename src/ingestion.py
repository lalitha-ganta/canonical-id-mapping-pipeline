
import pandas as pd
from pathlib import Path

# Define input CSV file location
FILE_PATH = Path("data/input/customers.csv")


def read_customer_data():

    # Check whether the file exists
    if not FILE_PATH.exists():
        print("Error: Customer CSV file not found!")
        return None

    # Read the CSV file using Pandas
    df = pd.read_csv(FILE_PATH, dtype=str)

    # Display the records
    print("Customer data loaded successfully!")

    print("\nTotal records:", len(df))

    print("\nCustomer records:")
    print(df.to_string(index=False))

    return df


if __name__ == "__main__":
    read_customer_data()
