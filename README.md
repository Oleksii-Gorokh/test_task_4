# Registration Port

Python port of a legacy student registration screen. The project implements
`drop`, `add`, and `swap` operations over SQLite while keeping the data access,
business logic, and CLI layers separated.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
```

## Run

Create a local database from the SQL scripts:

```bash
python -c "from registration_port.db import initialize_database; initialize_database('registration.sqlite3', 'data/schema.sqlite.sql', 'data/seed.sqlite.sql')"
```

Run the CLI:

```bash
python -m registration_port --database registration.sqlite3 drop 1001 CS101-01 2024 S
python -m registration_port --database registration.sqlite3 add 1007 CS101-02 2024 S
python -m registration_port --database registration.sqlite3 swap 1001 CS101-01 CS201-01 2024 S
```

## Tests

```bash
python -m pytest
```

## Project Structure

```text
data/
  schema.sqlite.sql
  seed.sqlite.sql
src/registration_port/
  cli.py
  db.py
  results.py
  service.py
tests/
  conftest.py
  test_acceptance.py
  test_registration_service.py
```

## Implementation Notes

`db.py` contains SQLite queries and transaction handling without business
rules. `service.py` contains the registration rules, result codes, and the
required order of checks. `cli.py` only parses arguments, calls the service,
prints the exact message, and returns the expected exit code.

`swap` runs in a single transaction. If the second operation fails, the first
operation is rolled back. SQLite errors also roll back the whole transaction.
