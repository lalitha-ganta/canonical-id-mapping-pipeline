# Canonical ID Mapping Pipeline

## Project Overview

A Python-based Data Engineering solution that maps customer identifiers from multiple source systems (CRM, WEBSITE, and APP) to canonical customer IDs.

Built for the YottaFlex AI 72-Hour Code Challenge.

## Technologies Used

- Python
- pandas
- SQLite
- pytest

## Architecture

```text
Customer CSV
     |
     v
Data Ingestion
     |
     v
Data Validation
     |
     +----> Rejected Records
     |
     +----> Unresolved Records
     |
     v
SQLite Database
     |
     v
Canonical ID Matching
     |
     +----> Mapping Conflicts
     |
     v
Canonical ID Mappings
     |
     v
Mapping History
```

## Features

- CSV data ingestion
- Schema and email validation
- Duplicate detection
- Exact and rule-based canonical ID matching
- One-to-many conflict detection
- Mapping history tracking
- Unresolved mapping tracking
- Idempotent ingestion
- Pipeline run logging
- Automated testing
- Performance benchmarking

## Installation

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the Project

Initialize the database:

```powershell
python -m src.database
```

Load customer records:

```powershell
python -m src.loader
```

Run canonical matching:

```powershell
python -m src.matching
```

Verify reconciliation:

```powershell
python -m src.verify_reconciliation
```

## Automated Testing

```powershell
python -m pytest tests/ -v
```

Latest observed result: 11 tests passed.

## Performance Benchmark

Generate 100,000 synthetic customer records:

```powershell
python -m src.generate_large_dataset
```

Run benchmark:

```powershell
python -m src.benchmark
```

### Benchmark Results

| Metric | Result |
|---|---|
| Input records | 100,000 |
| CSV reading time | 0.203 seconds |
| Validation time | 14.790 seconds |
| Total processing time | 14.994 seconds |
| Throughput | 6,669.45 records/second |
| Reconciliation | PASSED |

The benchmark covers CSV reading and validation, excluding database loading and matching.

## Sample Data Results

| Metric | Count |
|---|---:|
| Total input records | 8 |
| Accepted records | 7 |
| Rejected records | 1 |
| Unresolved records | 1 |
| Matchable records | 6 |

## Design Decisions

SQLite was selected for simple local execution without external infrastructure.

Deterministic record IDs and database constraints support safe reruns.

Mapping history and conflict tables provide traceability.

## Known Limitations

- SQLite is intended for local demonstration.
- Validation uses row-by-row processing.
- The performance benchmark excludes database insertion and canonical matching.
- Further testing is needed for late-arriving data and matching-rule precedence.

## Future Improvements

- Vectorized pandas validation
- Configurable matching rules
- End-to-end performance testing
- Automated CI/CD testing
- Cloud database integration

## Documentation

- `docs/data_dictionary.md`
- `docs/design_notes.md`
- `docs/performance_report.md`
