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



