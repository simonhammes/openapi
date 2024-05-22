import os
import pytest
import requests
import schemathesis
from schemathesis import Case

# TODO: Read from environment
BASE_URL = 'https://seatable-demo.de'
USERNAME = os.environ.get('SEATABLE_USERNAME')
PASSWORD = os.environ.get('SEATABLE_PASSWORD')

assert USERNAME is not None, 'SEATABLE_USERNAME environment variable is not set'
assert PASSWORD is not None, 'SEATABLE_PASSWORD environment variable is not set'

# TODO: Get WORKSPACE_ID from somewhere else
WORKSPACE_ID = 2
BASE_NAME = 'Automated Tests'

schema = schemathesis.from_path('./user_account_operations.yaml', base_url=BASE_URL, validate_schema=True)

@pytest.fixture
def account_token():
    data = {
        "username": USERNAME,
        "password": PASSWORD,
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded"
    }

    # TODO: Use schemathesis for this request
    response = requests.post(f'{BASE_URL}/api2/auth-token/', data=data, headers=headers)

    assert response.status_code == 200

    account_token = response.json()['token']

    assert isinstance(account_token, str)

    yield account_token

@pytest.fixture
def base(account_token: str):
    body = {
        "workspace_id": WORKSPACE_ID,
        "name": BASE_NAME,
    }
    case: Case = schema.get_operation_by_id('createBase').make_case(body=body)
    response = case.call_and_validate(headers={"Authorization": f"Bearer {account_token}"})

    assert response.status_code == 201

    # TODO: Prune existing rows?

    base_id = response.json()["table"]["id"]
    assert isinstance(base_id, int)

    yield base_id

    # Delete base to not cause any issues on future test runs
    path_parameters = {'workspace_id': WORKSPACE_ID}
    body = {'name': BASE_NAME}
    case: Case = schema.get_operation_by_id('deleteBase').make_case(path_parameters=path_parameters, body=body)
    response = case.call_and_validate(headers={"Authorization": f"Bearer {account_token}"})

    assert response.status_code == 200

def test_add_table(base):
    assert True
