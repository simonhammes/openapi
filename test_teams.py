import os
import secrets
import string
from typing import Generator
import pytest
import schemathesis
from dataclasses import dataclass, field
from random import randint
from requests import Response
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.json import JSONSnapshotExtension
from syrupy.matchers import path_type

# TODO: Make sure credentials are never logged to the console (in case of exceptions/assertion errors)
# https://github.com/pytest-dev/pytest/issues/8613

# TODO: Read from environment
BASE_URL = 'https://seatable-demo.de'
ADMIN_USERNAME = os.environ.get('SEATABLE_ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('SEATABLE_ADMIN_PASSWORD')

assert ADMIN_USERNAME is not None, 'SEATABLE_ADMIN_USERNAME environment variable is not set'
assert ADMIN_PASSWORD is not None, 'SEATABLE_ADMIN_PASSWORD environment variable is not set'

authentication_schema = schemathesis.from_path('./authentication.yaml', base_url=BASE_URL, validate_schema=True)
system_admin_account_operations = schemathesis.from_path('./system_admin_account_operations.yaml', base_url=BASE_URL, validate_schema=True)
team_admin_account_operations = schemathesis.from_path('./team_admin_account_operations.yaml', base_url=BASE_URL, validate_schema=True)

# TODO: Disable redirects for all tests? (to prevent issues like https://forum.seatable.io/t/seatable-4-4-out-now/4237/4)

def generate_password() -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(20))

@schemathesis.hook
def after_call(context, case, response: Response):
    # Log all request URLs. You have to run pytest with '-rA' in order to see these for successful tests.
    print(f'{response.request.method} {response.request.url}')

@dataclass
class TeamAdmin:
    """Class for storing team/org info"""
    team_id: int
    # Hide base token from console output by setting repr=False
    account_token: str = field(repr=False)

class Secret:
    """
    Class to store a secret, ensures that the value will not be printed (e.g. if an assertion fails)
    Based on https://github.com/pytest-dev/pytest/issues/8613#issuecomment-830011874
    """
    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return "Secret(********)"

    def __str___(self):
        return "*******"

@pytest.fixture
def snapshot_json(snapshot):
    # https://github.com/tophat/syrupy#jsonsnapshotextension
    return snapshot.use_extension(JSONSnapshotExtension)

# scope='module' ensures that this functions runs only once for all tests in this module
@pytest.fixture(scope='module')
def system_admin_account_token() -> Secret:
    body = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}

    operation = authentication_schema.get_operation_by_id('getAccountTokenfromUsername')
    case: Case = operation.make_case(body=body)
    response = case.call_and_validate()

    assert response.status_code == 200

    account_token = response.json()['token']
    assert isinstance(account_token, str)

    return Secret(account_token)

@pytest.fixture
def team(system_admin_account_token: Secret) -> Generator[int, None, None]:
    team_name = f'automated-testing-org-{randint(1, 10000)}'
    team_admin_email = 'automated-testing-team-admin@seatable.io'
    team_admin_password = generate_password()

    body = {
        'org_name': team_name,
        'admin_email': team_admin_email,
        'password': team_admin_password,
        'with_workspace': True,
    }
    case: Case = system_admin_account_operations.get_operation_by_id('addTeam').make_case(body=body)
    response = case.call_and_validate(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})

    assert response.status_code == 200

    team = response.json()
    team_id = team['org_id']
    assert isinstance(team_id, int)

    # Fetch account token for team admin
    body = {"username": team_admin_email, "password": team_admin_password}
    operation = authentication_schema.get_operation_by_id('getAccountTokenfromUsername')
    case: Case = operation.make_case(body=body)
    response = case.call_and_validate()

    assert response.status_code == 200

    account_token = response.json()['token']
    assert isinstance(account_token, str)

    yield TeamAdmin(team_id=team_id, account_token=account_token)

    path_parameters = {'org_id': team_id}
    case: Case = system_admin_account_operations.get_operation_by_id('deleteTeam').make_case(path_parameters=path_parameters)
    response = case.call_and_validate(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})

@pytest.fixture
def team_name(system_admin_account_token: Secret) -> Generator[str, None, None]:
    team_name = f'automated-testing-org-{randint(1, 10000)}'

    yield team_name

    # Remove team to not cause issues on future test runs
    case: Case = system_admin_account_operations.get_operation_by_id('listTeams').make_case()
    response = case.call_and_validate(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})
    data = response.json()

    assert response.status_code == 200

    # Find the organization we want to delete
    org_id = next((team['org_id'] for team in data['organizations'] if team['org_name'] == team_name), None)
    assert isinstance(org_id, int)

    path_parameters = {'org_id': org_id}
    case: Case = system_admin_account_operations.get_operation_by_id('deleteTeam').make_case(path_parameters=path_parameters)
    response = case.call_and_validate(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})

def test_addTeam(system_admin_account_token: Secret, team_name: str):
    # This test case uses the team_name() fixture to make sure that the added team is automatically cleaned up after this test case

    body = {
        'org_name': team_name,
        'admin_email': 'automated-testing-team-admin@seatable.io',
        'password': generate_password(),
        'with_workspace': True,
    }
    case: Case = system_admin_account_operations.get_operation_by_id('addTeam').make_case(body=body)
    response = case.call_and_validate(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})

    assert response.status_code == 200

def test_updateTeam_modify_role(system_admin_account_token: Secret, team: TeamAdmin):
    path_parameters = {'org_id': team.team_id}
    body = {'role': 'org_enterprise'}
    case: Case = system_admin_account_operations.get_operation_by_id('updateTeam').make_case(path_parameters=path_parameters, body=body)
    response = case.call_and_validate(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})

    assert response.status_code == 200

    team = response.json()

    assert team['role'] == 'org_enterprise'

def test_addTeamUser(system_admin_account_token: Secret, team: TeamAdmin):
    path_parameters = {'org_id': team.team_id}
    body = {
        'email': 'automated-testing-user-1@seatable.io',
        'password': generate_password(),
        'name': 'automated-testing-user-1',
    }
    case: Case = system_admin_account_operations.get_operation_by_id('addTeamUser').make_case(path_parameters=path_parameters, body=body) 
    response = case.call_and_validate(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})

    assert response.status_code == 200

def test_updateUser(team: TeamAdmin):
    user = add_user(team, username='automated-testing-user-test_updateUser')

    # Internal ...@auth.local email address
    user_email = user['email']
    assert isinstance(user_email, str)

    path_parameters = {'org_id': team.team_id, 'user_id': user_email}
    body = {'name': 'updated-name'}
    case: Case = team_admin_account_operations.get_operation_by_id('updateUser').make_case(path_parameters=path_parameters, body=body)
    response = case.call_and_validate(headers={'Authorization': f'Bearer {team.account_token}'})

    assert response.status_code == 200

    user = response.json()
    assert user['name'] == 'updated-name'

def test_listTeamUsers(team: TeamAdmin, snapshot_json: SnapshotAssertion):
    path_parameters = {'org_id': team.team_id}
    case: Case = team_admin_account_operations.get_operation_by_id('listTeamUsers').make_case(path_parameters=path_parameters)
    response = case.call_and_validate(headers={'Authorization': f'Bearer {team.account_token}'})

    assert response.status_code == 200

    data = response.json()
    assert len(data['user_list']) == 1

    matcher = path_type(
        {
            # Exclude unstable props from value comparison and just store their types
            r"user_list\..*\.(ctime|email|name)": (str,),
            r"user_list\..*\.(id|workspace_id)": (int,),
        },
        regex=True,
    )
    assert snapshot_json(matcher=matcher) == data

def add_user(team: TeamAdmin, username) -> dict:
    path_parameters = {'org_id': team.team_id}
    body = {
        'email': f'{username}@seatable.io',
        'password': generate_password(),
        'name': username,
    }
    case: Case = team_admin_account_operations.get_operation_by_id('addUser').make_case(path_parameters=path_parameters, body=body) 
    response = case.call_and_validate(headers={'Authorization': f'Bearer {team.account_token}'})

    assert response.status_code == 200

    return response.json()
