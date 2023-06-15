# Codemaze

## Install Requirements

Install all requirements by going to the root folder and running:

```bash
pip install -r requirements.txt
```

## Running

The environment var `CODEMAZE_KEY` must be set with the secret that will be used to generate JWTs.

### As debug (localhost:48345)

The environment var `DEBUG_DB_STRING` must be set with the debug database string or an exception will be raised.

Navigate to code folder and run:

```bash
python app.py
```

### Tests

The environment var `TEST_DB_STRING` must be set with the testing database string or an exception will be raised.

## Modelling

### Entity-Relationship Diagram (ERD)

![entity-relationship](./metadata/diagrama.png)

### Data-Structure diagram (DSD)

![data-structure](./metadata/logico.png)
