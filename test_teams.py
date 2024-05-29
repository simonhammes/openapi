import schemathesis
from .conftest import BASE_URL, generate_password, Secret, TeamAdmin
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type

authentication_schema = schemathesis.from_path('./authentication.yaml', base_url=BASE_URL, validate_schema=True)
system_admin_account_operations = schemathesis.from_path('./system_admin_account_operations.yaml', base_url=BASE_URL, validate_schema=True)
team_admin_account_operations = schemathesis.from_path('./team_admin_account_operations.yaml', base_url=BASE_URL, validate_schema=True)

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
