import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")

files = sorted(DATA_DIR.glob("*.csv"))

print("=" * 70)
print("OLIST E-COMMERCE DATASET INSPECTION")
print("=" * 70)

print(f"\nCSV files found: {len(files)}")

for file in files:
    print("\n" + "-" * 70)
    print(f"FILE: {file.name}")
    print("-" * 70)

    df = pd.read_csv(file)

    print(f"Rows       : {df.shape[0]:,}")
    print(f"Columns    : {df.shape[1]}")

    print("\nColumn names:")
    for column in df.columns:
        print(f"  - {column}")

    print("\nMissing values:")
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)

    if len(missing) == 0:
        print("  No missing values")
    else:
        for column, count in missing.items():
            percentage = (count / len(df)) * 100
            print(f"  {column}: {count:,} ({percentage:.2f}%)")

    print(f"\nDuplicate rows: {df.duplicated().sum():,}")

print("\n" + "=" * 70)
print("INSPECTION COMPLETED")
print("=" * 70)