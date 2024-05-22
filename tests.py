import os
import pytest
import schemathesis
from dataclasses import dataclass, field
from requests import Response
from schemathesis import Case
from syrupy.extensions.json import JSONSnapshotExtension
from syrupy.filters import props
from syrupy.matchers import path_type
from unittest import mock

# TODO: Make sure credentials are never logged to the console (in case of exceptions/assertion errors)
# https://github.com/pytest-dev/pytest/issues/8613

# TODO: Read from environment
BASE_URL = 'https://seatable-demo.de'
USERNAME = os.environ.get('SEATABLE_USERNAME')
PASSWORD = os.environ.get('SEATABLE_PASSWORD')

assert USERNAME is not None, 'SEATABLE_USERNAME environment variable is not set'
assert PASSWORD is not None, 'SEATABLE_PASSWORD environment variable is not set'

# TODO: Get WORKSPACE_ID from somewhere else
WORKSPACE_ID = 2
# TODO: BASE_NAME with included GHA run ID to aid debugging?
BASE_NAME = 'Automated Tests'

schema = schemathesis.from_path('./user_account_operations.yaml', base_url=BASE_URL, validate_schema=True)
authentication_schema = schemathesis.from_path('./authentication.yaml', base_url=BASE_URL, validate_schema=True)
# TODO: Use non-deprecated version?
base_operations_schema = schemathesis.from_path('./base_operations_deprecated.yaml', base_url=BASE_URL, validate_schema=True)

# TODO: Disable redirects for all tests? (to prevent issues like https://forum.seatable.io/t/seatable-4-4-out-now/4237/4)

@schemathesis.hook
def after_call(context, case, response: Response):
    # Log all request URLs. You have to run pytest with '-rA' in order to see these for successful tests.
    print(response.request.url)

@dataclass
class Base:
    """Class for storing base info"""
    uuid: str
    # Hide base token from console output by setting repr=False
    token: str = field(repr=False)

@pytest.fixture
def snapshot_json(snapshot):
    # https://github.com/tophat/syrupy#jsonsnapshotextension
    return snapshot.use_extension(JSONSnapshotExtension)

# scope='module' ensures that this functions runs only once for all tests in this module
@pytest.fixture(scope='module')
def account_token() -> str:
    body = {"username": USERNAME, "password": PASSWORD}

    operation = authentication_schema.get_operation_by_id('getAccountTokenfromUsername')
    case: Case = operation.make_case(body=body)
    response = case.call_and_validate()

    assert response.status_code == 200

    account_token = response.json()['token']
    assert isinstance(account_token, str)

    return account_token

@pytest.fixture(scope='module')
def base(account_token: str):
    body = {"workspace_id": WORKSPACE_ID, "name": BASE_NAME}
    case: Case = schema.get_operation_by_id('createBase').make_case(body=body)
    response = case.call_and_validate(headers={"Authorization": f"Bearer {account_token}"})

    assert response.status_code == 201

    # TODO: Prune existing rows?

    base_uuid = response.json()["table"]["uuid"]
    assert isinstance(base_uuid, str)

    path_parameters = {'workspace_id': WORKSPACE_ID, 'base_name': BASE_NAME}
    headers = {'Authorization': f'Bearer {account_token}'}

    operation = authentication_schema.get_operation_by_id('getBaseTokenWithAccountToken')
    case: Case = operation.make_case(path_parameters=path_parameters, headers=headers)
    response = case.call_and_validate()

    assert response.status_code == 200

    base_token = response.json()['access_token']
    assert isinstance(base_token, str)

    yield Base(base_uuid, base_token)

    # Delete base to not cause any issues on future test runs
    path_parameters = {'workspace_id': WORKSPACE_ID}
    body = {'name': BASE_NAME}

    case: Case = schema.get_operation_by_id('deleteBase').make_case(path_parameters=path_parameters, body=body)
    response = case.call_and_validate(headers={"Authorization": f"Bearer {account_token}"})

    assert response.status_code == 200

COLUMNS = [
    {
        'column_name': 'text',
        'column_type': 'text',
    },
    {
        'column_name': 'long-text',
        'column_type': 'long-text',
    },
    {
        'column_name': 'number',
        'column_type': 'number',
        # TODO: Add different test cases for different column_data values (format, decimal, thousands)
    },
    {
        'column_name': 'collaborator',
        'column_type': 'collaborator',
    },
    {
        'column_name': 'date-iso',
        'column_type': 'date',
        'column_data': {
            'format': 'YYYY-MM-DD'
        }
    },
    {
        'column_name': 'date-iso-hours-minutes',
        'column_type': 'date',
        'column_data': {
            'format': 'YYYY-MM-DD HH:mm'
        }
    },
    {
        'column_name': 'date-german',
        'column_type': 'date',
        'column_data': {
            'format': 'DD.MM.YYYY'
        }
    },
    {
        'column_name': 'date-german-hours-minutes',
        'column_type': 'date',
        'column_data': {
            'format': 'DD.MM.YYYY HH:mm'
        }
    },
    {
        'column_name': 'single-select',
        'column_type': 'single-select',
        'column_data': {
            'options': [
               {'id': 1, 'name': 'option-1', 'color': '#9860E5'},
               {'id': 2, 'name': 'option-2', 'color': '#89D2EA'},
               {'id': 3, 'name': 'option-3', 'color': '#59CB74'},
            ]
        }
    },
    {
        'column_name': 'multiple-select',
        'column_type': 'multiple-select',
        'column_data': {
            'options': [
               {'id': 1, 'name': 'option-1', 'color': '#9860E5'},
               {'id': 2, 'name': 'option-2', 'color': '#89D2EA'},
               {'id': 3, 'name': 'option-3', 'color': '#59CB74'},
            ]
        }
    },
    {
        'column_name': 'checkbox',
        'column_type': 'checkbox',
    },
    {
        'column_name': 'formula',
        'column_type': 'formula',
        'column_data': {
            'formula': "dateAdd({date-iso}, 1, 'year')"
        }
    },
    # TODO: Link + Link Formula
    # TODO: creator + last-modifier
    # {
    #     'column_name': 'creator',
    #     'column_type': 'creator',
    # },
    # {
    #     'column_name': 'last-modifier',
    #     'column_type': 'last-modifier',
    # },
]

ROWS = [
    {
        'text': 'ABC',
        'long-text': '## Heading\n- Item 1\n- Item 2',
        'number': 499.99,
        # TODO
        # 'collaborator':
        'date-iso': '2030/06/20',
        'date-iso-hours-minutes': '2030/06/20 23:55',
        'date-german': '20.06.2030',
        'date-german-hours-minutes': '20.06.2030 23:55',
        'single-select': 'option-1',
        'multiple-select': ['option-1', 'option-2'],
        'checkbox': True,
    },
    {
        'text': 'D',
        'long-text': '## Heading\n- Item 1\n- Item 2',
        'number': 500,
        # TODO
        # 'collaborator':
        'date-iso': '2030/06/20',
        'date-iso-hours-minutes': '2030/06/20 23:55',
        'date-german': '20.06.2030',
        'date-german-hours-minutes': '20.06.2030 23:55',
        'single-select': 'option-2',
        'multiple-select': ['option-2', 'option-3'],
        'checkbox': False,
    },
    {
        'text': 'E',
        'long-text': '## Heading\n- Item 1\n- Item 2',
        'number': -10,
        # TODO
        # 'collaborator':
        'date-iso': '2030/06/20',
        'date-iso-hours-minutes': '2030/06/20 23:55',
        'date-german': '20.06.2030',
        'date-german-hours-minutes': '20.06.2030 23:55',
        'single-select': 'option-3',
        'multiple-select': ['option-1', 'option-2', 'option-3'],
        'checkbox': True,
    },
    {
        # Regression test for https://forum.seatable.io/t/python-modification-in-rows-data-since-4-4/4254
        'text': 'row-with-empty-values'
    }
]

def test_get_row(base: Base, snapshot_json):
    table_name = 'test_get_row'

    create_table(base, table_name, COLUMNS)

    row = {
        'text': 'ABC',
        'long-text': '## Heading\n- Item 1\n- Item 2',
        'number': 499.99,
        # TODO
        # 'collaborator':
        'date-iso': '2030/06/20',
        'date-iso-hours-minutes': '2030/06/20 23:55',
        'date-german': '20.06.2030',
        'date-german-hours-minutes': '20.06.2030 23:55',
        'checkbox': True,
    }
    row_id = add_row(base, table_name, row)

    path_parameters = {'base_uuid': base.uuid, 'row_id': row_id}
    query = {'table_name': table_name}
    headers = {'Authorization': f'Bearer {base.token}'}

    operation = base_operations_schema.get_operation_by_id('getRowDeprecated')
    case: Case = operation.make_case(path_parameters=path_parameters, query=query, headers=headers)

    response = case.call_and_validate()

    assert response.status_code == 200

    # Configure a custom matcher since some values will always change
    matcher = path_type({
        '_id': (str,),
        '_ctime': (str,),
        '_mtime': (str,),
    })

    assert snapshot_json(matcher=matcher) == response.json()

# Expected rows for test_list_rows and test_list_rows_with_sql
EXPECTED_ROWS = [
    {'_id': mock.ANY, '_mtime': mock.ANY, '_ctime': mock.ANY, 'text': 'ABC', 'long-text': '## Heading\n- Item 1\n- Item 2', 'number': 499.99, 'date-iso': '2030-06-20', 'date-iso-hours-minutes': '2030-06-20 23:55', 'date-german': '2030-06-20', 'date-german-hours-minutes': '2030-06-20 23:55', 'single-select': 'option-1', 'multiple-select': ['option-1', 'option-2'], 'checkbox': True, 'formula': '2031-06-20'},
    {'_id': mock.ANY, '_mtime': mock.ANY, '_ctime': mock.ANY, 'text': 'D', 'long-text': '## Heading\n- Item 1\n- Item 2', 'number': 500, 'date-iso': '2030-06-20', 'date-iso-hours-minutes': '2030-06-20 23:55', 'date-german': '2030-06-20', 'date-german-hours-minutes': '2030-06-20 23:55', 'single-select': 'option-2', 'multiple-select': ['option-2', 'option-3'], 'checkbox': False, 'formula': '2031-06-20'},
    {'_id': mock.ANY, '_mtime': mock.ANY, '_ctime': mock.ANY, 'text': 'E', 'long-text': '## Heading\n- Item 1\n- Item 2', 'number': -10, 'date-iso': '2030-06-20', 'date-iso-hours-minutes': '2030-06-20 23:55', 'date-german': '2030-06-20', 'date-german-hours-minutes': '2030-06-20 23:55', 'single-select': 'option-3', 'multiple-select': ['option-1', 'option-2', 'option-3'], 'checkbox': True, 'formula': '2031-06-20'},
    # Make sure that empty values are not returned
    # Regression test for https://forum.seatable.io/t/python-modification-in-rows-data-since-4-4/4254
    {'_id': mock.ANY, '_mtime': mock.ANY, '_ctime': mock.ANY, 'text': 'row-with-empty-values', 'formula': '#VALUE!'}
]

def test_list_rows(base: Base, snapshot_json):
    table_name = 'test_list_rows'

    create_table(base, table_name, COLUMNS)
    append_rows(base, table_name, ROWS)

    path_parameters = {'base_uuid': base.uuid}
    query = {'table_name': table_name}
    headers = {'Authorization': f'Bearer {base.token}'}

    operation = base_operations_schema.get_operation_by_id('listRowsDeprecated')
    case: Case = operation.make_case(path_parameters=path_parameters, query=query, headers=headers)

    response = case.call_and_validate()

    assert response.status_code == 200

    # Verify that response matches snapshot while excluding _id, _ctime and _mtime properties
    assert snapshot_json(exclude=props('_id', '_ctime', '_mtime')) == response.json()

def test_list_rows_with_sql(base: Base, snapshot_json):
    table_name = 'test_list_rows_with_sql'

    create_table(base, table_name, COLUMNS)
    append_rows(base, table_name, ROWS)

    path_parameters = {'base_uuid': base.uuid}
    body = {'sql': f'SELECT * FROM {table_name}', 'convert_keys': True}
    headers = {'Authorization': f'Bearer {base.token}'}

    operation = base_operations_schema.get_operation_by_id('querySQLDeprecated')
    case: Case = operation.make_case(path_parameters=path_parameters, body=body, headers=headers)

    # TODO: case.call_and_validate() causes a schema violation error (expected object; the API returned an array)
    response = case.call()

    assert response.status_code == 200

    # TODO: Verify excluded props
    assert snapshot_json(exclude=props('_id', '_ctime', '_mtime', 'key', 'base_id', 'table_id')) == response.json()

def create_table(base: Base, table_name: str, columns: list[dict]):
    path_parameters = {'base_uuid': base.uuid}
    body = {'table_name': table_name, 'columns': columns}
    headers = {'Authorization': f'Bearer {base.token}'}

    operation = base_operations_schema.get_operation_by_id('createTableDeprecated')
    case: Case = operation.make_case(path_parameters=path_parameters, body=body, headers=headers)

    # TODO: case.call_and_validate() causes a schema violation error (expected object; the API returned an array)
    response = case.call()

    assert response.status_code == 200

def add_row(base: Base, table_name: str, row: dict) -> str:
    path_parameters = {'base_uuid': base.uuid}
    body = {'table_name': table_name, 'row': row}
    headers = {'Authorization': f'Bearer {base.token}'}

    operation = base_operations_schema.get_operation_by_id('addRowDeprecated')
    case: Case = operation.make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call_and_validate()

    row_id = response.json()['_id']
    assert isinstance(row_id, str)

    return row_id

def append_rows(base: Base, table_name: str, rows: list[dict]):
    path_parameters = {'base_uuid': base.uuid}
    body = {'table_name': table_name, 'rows': rows}
    headers = {'Authorization': f'Bearer {base.token}'}

    operation = base_operations_schema.get_operation_by_id('appendRowsDeprecated')
    case: Case = operation.make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call_and_validate()

    assert response.status_code == 200
