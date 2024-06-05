import pytest
import schemathesis
from .conftest import Base, BASE_URL, Secret
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type

schema = schemathesis.from_path('./user_account_operations.yaml', base_url=BASE_URL, validate_schema=True)
base_operations_deprecated_schema= schemathesis.from_path('./base_operations_deprecated.yaml', base_url=BASE_URL, validate_schema=True)
base_operations_schema = schemathesis.from_path('./base_operations.yaml', base_url=BASE_URL, validate_schema=True)

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
        'column_name': 'date-us',
        'column_type': 'date',
        'column_data': {
            'format': 'M/D/YYYY'
        }
    },
    {
        'column_name': 'date-us-hours-minutes',
        'column_type': 'date',
        'column_data': {
            'format': 'M/D/YYYY HH:mm'
        }
    },
        {
        'column_name': 'date-european',
        'column_type': 'date',
        'column_data': {
            'format': 'DD/MM/YYYY'
        }
    },
    # FIXME: Fix this
    # Also fails with insertColumn operation on api.seatable.io: {"error_type": "column_data_error", "error_message": "column_data: {\"format\":\"DD/MM/YYYY HH:mm\"} do not meet specifications."}
    #{
    #     'column_name': 'date-european-hours-minutes',
    #     'column_type': 'date',
    #     'column_data': {
    #         'format': 'DD/MM/YYYY HH:mm'
    #     }
    #},
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
        'column_name': 'duration-hours-minutes',
        'column_type': 'duration',
        'column_data': {
            'format': 'duration',
            'duration_format': 'h:mm'
        }
    },
    {
        'column_name': 'duration-hours-minutes-seconds',
        'column_type': 'duration',
        'column_data': {
            'format': 'duration',
            'duration_format': 'h:mm:ss'
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
    # TODO: image
    # TODO: file
    {
        'column_name': 'email',
        'column_type': 'email',
    },
    {
        'column_name': 'url',
        'column_type': 'url',
    },
    {
        'column_name': 'checkbox',
        'column_type': 'checkbox',
    },
    {
        'column_name': 'rate',
        'column_type': 'rate',
        'column_data': {
            'rate_max_number': 10,
        },
    },
    {
        'column_name': 'formula',
        'column_type': 'formula',
        'column_data': {
            'formula': "dateAdd({date-iso}, 1, 'year')"
        }
    },
    {
        'column_name': 'formula-integer-return-value',
        'column_type': 'formula',
        'column_data': {
            'formula': '1 + 2',
        },
    },
    {
        'column_name': 'formula-float-return-value',
        'column_type': 'formula',
        'column_data': {
            'formula': '1.3 + 2.6',
        },
    },
    {
        'column_name': 'formula-boolean-return-value',
        'column_type': 'formula',
        'column_data': {
            'formula': 'and(true(), false())',
        },
    },
    # TODO: Link + Link Formula
    {
        'column_name': 'geolocation-country-region',
        'column_type': 'geolocation',
        'column_data': {
            'geo_format': 'country_region',
            'lang': 'en',
        },
    },
    {
        'column_name': 'geolocation-lat-lon',
        'column_type': 'geolocation',
        'column_data': {
            'geo_format': 'lng_lat',
        },
    },
    # TODO: creator + last-modifier
    # {
    #     'column_name': 'creator',
    #     'column_type': 'creator',
    # },
    # {
    #     'column_name': 'last-modifier',
    #     'column_type': 'last-modifier',
    # },
    {
        'column_name': 'auto-number-integer',
        'column_type': 'auto-number',
        'column_data': {
            'format': '0000',
            'digits': 4,
        },
    },
    {
        'column_name': 'auto-number-string-prefix',
        'column_type': 'auto-number',
        'column_data': {
            'format': '0000',
            'digits': 4,
            'prefix_type': 'string',
            'prefix': 'row',
        },
    },
    {
        'column_name': 'auto-number-date-prefix',
        'column_type': 'auto-number',
        'column_data': {
            'format': '0000',
            'digits': 4,
            'prefix_type': 'date',
        },
    },
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
        'date-us': '6/5/2024',
        'date-us-hours-minutes': '6/5/2024 23:55',
        'date-european': '05/06/2024',
        'date-european-hours-minutes': '05/06/2024 23:55',
        'date-german': '20.06.2030',
        'date-german-hours-minutes': '20.06.2030 23:55',
        # Duration values are in seconds
        'duration-hours-minutes': '5400',
        'duration-hours-minutes-seconds': '5430',
        'single-select': 'option-1',
        'multiple-select': ['option-1', 'option-2'],
        'email': 'example@seatable.io',
        'url': 'https://seatable.io',
        'checkbox': True,
        'rate': 7,
        'geolocation-country-region': {'country_region': 'Germany'},
        'geolocation-lat-lon': {'lng': 8.23, 'lat': 50.00},
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

def test_createBase(workspace_id: int, account_token: Secret, snapshot_json: SnapshotAssertion):
    body = {"workspace_id": workspace_id, "name": 'automated-testing-ahSh2sot'}
    case: Case = schema.get_operation_by_id('createBase').make_case(body=body)
    response = case.call_and_validate(headers={"Authorization": f"Bearer {account_token.value}"})

    assert response.status_code == 201

    matcher = path_type({
        'table.created_at': (str,),
        'table.id': (int,),
        'table.updated_at': (str,),
        'table.uuid': (str,),
        'table.workspace_id': (int,),
    })

    assert snapshot_json(matcher=matcher) == response.json()

@pytest.mark.parametrize('operation_id', ['createTable', 'createTableDeprecated'])
def test_createTable(base: Base, snapshot_json: SnapshotAssertion, operation_id: str):
    table_name = f'test_{operation_id}'

    path_parameters = {'base_uuid': base.uuid}
    body = {'table_name': table_name, 'columns': COLUMNS}
    headers = {'Authorization': f'Bearer {base.token}'}

    if operation_id == 'createTable':
        operation = base_operations_schema.get_operation_by_id('createTable')
    elif operation_id == 'createTableDeprecated':
        operation = base_operations_deprecated_schema.get_operation_by_id('createTableDeprecated')

    case: Case = operation.make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call_and_validate()

    assert response.status_code == 200

    matcher = path_type(
        {
            "_id": (str,),
            r"columns\..*\.key": (str,),
        },
        regex=True,
    )

    assert snapshot_json(matcher=matcher) == response.json()

@pytest.mark.parametrize('operation_id', ['appendRowsDeprecated', 'appendRows'])
def test_appendRows(base: Base, snapshot_json: SnapshotAssertion, operation_id: str):
    table_name = f'test_{operation_id}'

    create_table(base, table_name, COLUMNS)

    path_parameters = {'base_uuid': base.uuid}
    body = {'table_name': table_name, 'rows': ROWS}
    headers = {'Authorization': f'Bearer {base.token}'}

    if operation_id == 'appendRowsDeprecated':
        operation = base_operations_deprecated_schema.get_operation_by_id(operation_id)
    elif operation_id == 'appendRows':
        operation = base_operations_schema.get_operation_by_id(operation_id)

    case: Case = operation.make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call_and_validate()

    assert response.status_code == 200

    data = response.json()

    matcher = path_type(
        {
            'first_row': (dict,),
            r"row_ids\..*\._id": (str,),
        },
        regex=True
    )

    assert snapshot_json(matcher=matcher) == data

@pytest.mark.parametrize('operation_id', ['getRowDeprecated', 'getRow'])
def test_getRow(base: Base, snapshot_json, operation_id: str):
    table_name = f'test_{operation_id}'

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
    query = {'table_name': table_name, 'convert_keys': True}
    headers = {'Authorization': f'Bearer {base.token}'}

    if operation_id == 'getRowDeprecated':
        operation = base_operations_deprecated_schema.get_operation_by_id(operation_id)
    elif operation_id == 'getRow':
        operation = base_operations_schema.get_operation_by_id(operation_id)

    case: Case = operation.make_case(path_parameters=path_parameters, query=query, headers=headers)

    response = case.call_and_validate()

    assert response.status_code == 200

    # Configure a custom matcher since some values will always change
    matcher = path_type({
        '_id': (str,),
        '_ctime': (str,),
        '_mtime': (str,),
        '_creator': (str,),
        '_last_modifier': (str,),
        'auto-number-date-prefix': (str,),
    })

    assert snapshot_json(matcher=matcher) == response.json()

@pytest.mark.parametrize('operation_id', ['listRowsDeprecated', 'listRows'])
def test_listRows(base: Base, snapshot_json, operation_id: str):
    table_name = f'test_{operation_id}'

    create_table(base, table_name, COLUMNS)
    append_rows(base, table_name, ROWS)

    path_parameters = {'base_uuid': base.uuid}
    query = {'table_name': table_name, 'convert_keys': True}
    headers = {'Authorization': f'Bearer {base.token}'}

    if operation_id == 'listRowsDeprecated':
        operation = base_operations_deprecated_schema.get_operation_by_id(operation_id)
    elif operation_id == 'listRows':
        operation = base_operations_schema.get_operation_by_id(operation_id)

    case: Case = operation.make_case(path_parameters=path_parameters, query=query, headers=headers)

    response = case.call_and_validate()

    assert response.status_code == 200

    # Create a custom matcher to validate that certain fields contain
    # strings without storing their actual value since they are not stable
    matcher = path_type(
        {
            r"rows\..*\.(_id|_ctime|_mtime|_creator|_last_modifier|auto-number-date-prefix)": (str,),
        },
        regex=True,
    )

    # Verify that response matches snapshot
    assert snapshot_json(matcher=matcher) == response.json()

@pytest.mark.parametrize('operation_id', ['listRowsDeprecated', 'listRows'])
def test_listRows_links(base: Base,  snapshot_json: SnapshotAssertion, operation_id: str):
    table_name_1 = f'test_{operation_id}_links-1'
    columns_1 = [
        {'column_name': 'text', 'column_type': 'text'},
    ]
    create_table(base, table_name_1, columns_1)

    table_name_2 = f'test_{operation_id}_links-2'
    columns_2 = [
        {'column_name': 'text', 'column_type': 'text'},
    ]
    create_table(base, table_name_2, columns_2)

    # Add row to table 1
    table_1_row_id = add_row(base, table_name_1, {'text': 'Table 1 Row 1'})
    table_2_row_id = add_row(base, table_name_2, {'text': 'Table 2 Row 1'})

    # Insert link column
    path_parameters = {'base_uuid': base.uuid}
    body = {
        'table_name': table_name_2,
        'column_name': 'link',
        'column_type': 'link',
        'column_data': {
            'table': table_name_2,
            'other_table': table_name_1
        },
    }
    headers = {'Authorization': f'Bearer {base.token}'}
    case: Case = base_operations_deprecated_schema.get_operation_by_id('insertColumnDeprecated') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call_and_validate()

    link_id = response.json()['data']['link_id']
    assert isinstance(link_id, str)

    # Create row link
    body = {
        'table_name': table_name_1,
        'other_table_name': table_name_2,
        'link_id': link_id,
        'table_row_id': table_1_row_id,
        'other_table_row_id': table_2_row_id,
    }
    case: Case = base_operations_deprecated_schema.get_operation_by_id('createRowLinkDeprecated') \
        .make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call_and_validate()

    assert response.status_code == 200

    # List rows
    query = {'table_name': table_name_1, 'convert_keys': True}
    if operation_id == 'listRowsDeprecated':
        operation = base_operations_deprecated_schema.get_operation_by_id(operation_id)
    elif operation_id == 'listRows':
        operation = base_operations_schema.get_operation_by_id(operation_id)
    case: Case = operation.make_case(path_parameters=path_parameters, query=query, headers=headers)
    response = case.call_and_validate()

    matcher = path_type(
        {
            r"rows\..*\.(_id|_ctime|_mtime|_creator|_last_modifier)": (str,),
            r"rows\..*\.test_listRowsDeprecated_links-2.0": (str,),
            r"rows\..*\.test_listRows_links-2.*\.row_id": (str,),
        },
        regex=True,
    )

    # Verify that response matches snapshot
    assert snapshot_json(matcher=matcher) == response.json()

@pytest.mark.parametrize('operation_id', ['querySQLDeprecated', 'querySQL'])
def test_querySQL(base: Base, snapshot_json: SnapshotAssertion, operation_id: str):
    table_name = f'test_{operation_id}'

    create_table(base, table_name, COLUMNS)
    append_rows(base, table_name, ROWS)

    path_parameters = {'base_uuid': base.uuid}
    body = {'sql': f'SELECT * FROM {table_name}', 'convert_keys': True}
    headers = {'Authorization': f'Bearer {base.token}'}

    if operation_id == 'querySQLDeprecated':
        operation = base_operations_deprecated_schema.get_operation_by_id(operation_id)
    elif operation_id == 'querySQL':
        operation = base_operations_schema.get_operation_by_id(operation_id)

    case: Case = operation.make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call_and_validate()

    assert response.status_code == 200

    matcher = path_type(
        {
            # Exclude unstable props from value comparison and just store their types
            r"metadata\..*\.(base_id|key|table_id)": (str,),
            r"results\..*\.(_id|_ctime|_mtime|_creator|_last_modifier|auto-number-date-prefix)": (str,),
        },
        regex=True,
    )

    assert snapshot_json(matcher=matcher) == response.json()

def create_table(base: Base, table_name: str, columns: list[dict]):
    path_parameters = {'base_uuid': base.uuid}
    body = {'table_name': table_name, 'columns': columns}
    headers = {'Authorization': f'Bearer {base.token}'}

    operation = base_operations_deprecated_schema.get_operation_by_id('createTableDeprecated')
    case: Case = operation.make_case(path_parameters=path_parameters, body=body, headers=headers)

    response = case.call_and_validate()

    assert response.status_code == 200

def add_row(base: Base, table_name: str, row: dict) -> str:
    path_parameters = {'base_uuid': base.uuid}
    body = {'table_name': table_name, 'row': row}
    headers = {'Authorization': f'Bearer {base.token}'}

    operation = base_operations_deprecated_schema.get_operation_by_id('addRowDeprecated')
    case: Case = operation.make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call_and_validate()

    row_id = response.json()['_id']
    assert isinstance(row_id, str)

    return row_id

def append_rows(base: Base, table_name: str, rows: list[dict]):
    path_parameters = {'base_uuid': base.uuid}
    body = {'table_name': table_name, 'rows': rows}
    headers = {'Authorization': f'Bearer {base.token}'}

    operation = base_operations_deprecated_schema.get_operation_by_id('appendRowsDeprecated')
    case: Case = operation.make_case(path_parameters=path_parameters, body=body, headers=headers)
    response = case.call_and_validate()

    assert response.status_code == 200
