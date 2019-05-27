from unittest import mock
from anytimebot import persistence
from tinydb import TinyDB
from unittest import mock
import os
import pprint

def setup_function(function):
    """ setup any state tied to the execution of the given function.
    Invoked for every test function in the module.
    """
    os.remove(persistence.DB_FILE)
    persistence.init()

def teardown_function(function):
    """ teardown any state that was previously setup with a setup_function
    call.
    """
    persistence.db.close()


class MockUser:
    def __init__(self, id, name):
        self.id = id
        self.name = name


TEST_USER_NAME = "username"
TEST_SERVER_ID = "qwer1234"
TEST_TOURNAMENT_SIZE = 4

def test_is_username_used_yes():
    assert test_is_username_used()

def test_is_username_used_wrong_server_id():
    assert not test_is_username_used(server_id = TEST_SERVER_ID + 'a')

def test_is_username_used_wrong_size():
    assert not test_is_username_used(size = TEST_TOURNAMENT_SIZE + 1)

def test_is_username_used_running_status():
    assert not test_is_username_used(status = persistence.AnytimeStatus.RUNNING)

def test_is_username_used_completed_status():
    assert not test_is_username_used(status = persistence.AnytimeStatus.COMPLETED)

def test_is_username_used_wrong_name():
    assert not test_is_username_used(user_name = TEST_USER_NAME + 'a')

def test_is_username_used_wrong_user_id():
    assert test_is_username_used(user_id = TEST_USER_NAME + 'a')

def test_add_to_waiting_list_empty_db():
    persistence.add_to_waiting_list(
        TEST_SERVER_ID,
        MockUser(
            name = TEST_USER_NAME,
            id = TEST_USER_NAME
        ),
        TEST_TOURNAMENT_SIZE
    )

    all_requests = persistence.join_requests.all()
    assert len(all_requests) == 1
    request = all_requests[0]
    assert request['server_id'] == TEST_SERVER_ID
    assert request['user_id'] == TEST_USER_NAME
    assert request['user_name'] == TEST_USER_NAME
    assert request['tournament_size'] == TEST_TOURNAMENT_SIZE
    assert len(request['decks']) == 0

def test_add_to_waiting_list_previous_req():
    pass


# Helper functions
def test_is_username_used(
    server_id = TEST_SERVER_ID,
    size = TEST_TOURNAMENT_SIZE,
    status = persistence.AnytimeStatus.RECRUITING,
    user_name = TEST_USER_NAME,
    user_id = TEST_USER_NAME):

    persistence.anytimes.insert({
        'server_id': server_id,
        'size': size,
        'status': status,
        'players': [{
            'user_id': user_id,
            'user_name': user_name,
            'decks': None
        }]
    })

    return persistence.is_username_used(
        TEST_USER_NAME,
        TEST_SERVER_ID,
        TEST_TOURNAMENT_SIZE
    )
