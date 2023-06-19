# Codemaze

## Technologies
- Flask
- flask-restx
- SQLAlchemy
- SQLAlchemy-Utils
- PyJWT
- pytest

## Install Requirements

Install all requirements by going to the root folder and running:

```bash
make setup
```

## Running

The environment var `CODEMAZE_KEY` must be set with the secret that will be used to generate JWTs. It must be a 256 bit string and can be generated by running the following python script:

```python
import secrets

secrets.token_bytes(32)
```

### As debug (localhost:48345)

The environment var `DEBUG_DB_STRING` must be set with the debug database string or an exception will be raised.

Navigate to the root folder and run:

```bash
make run
```

### Tests

The environment var `TEST_DB_STRING` must be set with the testing database string or an exception will be raised.

## Modelling

### Entity-Relationship Diagram (ERD)

![entity-relationship](./metadata/diagrama.png)

### Data-Structure diagram (DSD)

![data-structure](./metadata/logico.png)
