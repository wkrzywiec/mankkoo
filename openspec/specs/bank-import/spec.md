# Spec: Bank Import

## Purpose

Defines how bank transaction CSV files are parsed and converted into account events.

---

## Requirements

### Requirement: Parse Bank CSV

The system SHALL parse CSV files exported by supported Polish banks.

#### Scenario: Import ING CSV
- **WHEN** a user uploads a CSV file exported from ING (PL)
- **THEN** the system parses it using the `PL_ING` importer
- **AND** produces rows with columns: `Account`, `Date`, `Title`, `Details`, `Category`, `Comment`, `Operation`, `Currency`, `Balance`

#### Scenario: Import mBank CSV
- **WHEN** a user uploads a CSV file exported from mBank (PL)
- **THEN** the system parses it using the `PL_MBANK` importer

#### Scenario: Import Millennium CSV
- **WHEN** a user uploads a CSV file exported from Millennium Bank (PL)
- **THEN** the system parses it using the `PL_MILLENIUM` importer

#### Scenario: Unsupported bank
- **WHEN** a user uploads a CSV from an unsupported bank
- **THEN** the system returns a clear error indicating the bank is not supported

---

### Requirement: Standard Column Output

The system SHALL normalize all bank CSV formats to a standard column set.

#### Scenario: Column order is guaranteed
- **WHEN** any bank CSV is parsed
- **THEN** the output DataFrame has columns in order: `Account`, `Date`, `Title`, `Details`, `Category`, `Comment`, `Operation`, `Currency`, `Balance`
- **AND** no extra columns appear

---

### Requirement: Store Imported Transactions as Events

The system SHALL convert parsed transactions into account events.

#### Scenario: Each transaction becomes an event
- **WHEN** a parsed CSV row represents a deposit (positive `Operation`)
- **THEN** a `MoneyDeposited` event is appended to the account stream

#### Scenario: Withdrawal transaction
- **WHEN** a parsed CSV row represents a withdrawal (negative `Operation`)
- **THEN** a `MoneyWithdrawn` event is appended to the account stream

---

### Requirement: File Upload via API

The system SHALL accept CSV file uploads from the frontend.

#### Scenario: Upload via multipart form
- **WHEN** the frontend uploads a file to `/api/accounts/{id}/import`
- **THEN** the backend receives the file as base64 bytes via `load_file_by_contents()`
- **AND** processes it through the appropriate bank importer
