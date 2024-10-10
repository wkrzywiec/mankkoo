# Accounting service

A heart of *mankkoo* responsible for data processing. Built with Python. 

## Requirements

* Python 3.10
* Poetry (version 1.3.2)

## Local work

* Install dependencies 

```bash
poetry install
```

* Run unit tests

```bash
poetry run pytest -s -vv --cov=./accounting
```

* Run the app

From within the `accounting` folder

```bash
poetry run flask run --reload
```

## Documentation

* Swagger UI - http://localhost:5000/docs
* OpenAPI 3 spec - http://localhost:5000/openapi.yaml

## Manual

Add new stream, e.g. for treasury bonds

```sql
insert into streams (id, type, version, metadata) values 
	(gen_random_uuid(), 'investment', 0, '{"active": true, "bankName": "PKO", "category": "treasury_bonds", "investmentName": "10-letnie obligacje EDO0734", "details": "6,80% w pierwszym rocznym okresie odsetkowym, w kolejnych rocznych okresach odsetkowych: marża 2,00% + inflacja; Wypłata odsetek: przy wykupie obligacji"}'::jsonb)
```

Add new event:

```sql
SELECT append_event(gen_random_uuid(), '{"units": 3,"balance": 300,"currency": "PLN","totalValue": 300,"pricePerUnit": 100}'::jsonb, 'TreasuryBondsBought'::text, 'a32a09bc-4907-48d6-96e8-989b70acd5c2'::uuid, 'investment'::text, to_timestamp('2024-01-01', 'YYYY-MM-DD')::timestamp without time zone at time zone 'Etc/UTC', 1::bigint)
```


