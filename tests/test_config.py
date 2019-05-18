from unittest import mock
from anytimebot import config


TEST_SERVER = 'Duel Links Meta'
TEST_SERVER_MISSING = f'{TEST_SERVER}1'
TEST_KEY = 'role'
TEST_KEY_MISSING = f'{TEST_KEY}1'
TEST_VALUE = 'Ticket 1'


def test_get_server_config_present():
    role = config.get_server_config(TEST_SERVER, TEST_KEY)
    assert role == TEST_VALUE


def test_get_server_config_absent():
    role = config.get_server_config(TEST_SERVER, TEST_KEY_MISSING)
    assert role is None


def test_get_server_config_missing_server():
    role = config.get_server_config(TEST_SERVER_MISSING, TEST_KEY)
    assert role == TEST_VALUE


def test_has_ticket_present():
    user = get_user_with_roles(['role1', 'role2', TEST_VALUE])
    assert config.has_ticket(TEST_SERVER, user)


def test_has_ticket_absent():
    user = get_user_with_roles(['role1', 'role2', 'role3'])
    assert not config.has_ticket(TEST_SERVER, user)


def test_has_ticket_missing_server():
    user = get_user_with_roles(['role1', 'role2', TEST_VALUE])
    assert config.has_ticket(TEST_SERVER_MISSING, user)


# Utils
def get_user_with_roles(role_names):
    user = mock.Mock(roles=[])
    for role_name in role_names:
        role = mock.Mock()
        role.configure_mock(name=role_name)
        user.roles.append(role)
    return user
