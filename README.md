# SeaTable OpenAPI

Welcome to the SeaTable OpenAPI Definition Repository! 🌊🔍✨

This repository encompasses all supported API calls for the SeaTable Server. The OpenAPI definition here serves two primary purposes:

1. Generate the online API reference accessible at https://api.seatable.io.
2. Generate the Postman collection, which is available at https://www.postman.com/seatable.

The repository is organized into version branches.

## Tests

This repository contains automated tests to detect possible regressions. The tests use [Schemathesis](https://schemathesis.readthedocs.io/en/stable/)
to extract information from the OpenAPI files and [pytest](https://docs.pytest.org/en/8.2.x/) to run the actual tests.

### Prerequisites

- Python 3.11
- pip
- Credentials for an account on [seatable-demo.de](https://seatable-demo.de)

### Set Up

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Export required environment variables
# The leading space makes sure they won't be part of your .bash_history
 export SEATABLE_USERNAME=''
 export SEATABLE_PASSWORD=''

# Run tests
# In case of any failures, run pytest with -vv for improved (but more verbose) output
pytest tests.py

# Deactivate virtual environment (optional)
deactivate
```
