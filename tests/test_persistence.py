from unittest import mock
from anytimebot import persistence
from tinydb import TinyDB
import os

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

TEST_USER_NAME = "username"
TEST_SERVER_ID = "qwer1234"
TEST_TOURNAMENT_SIZE = 4

def test_is_username_used():
    persistence.anytimes.insert({
        'server_id': TEST_SERVER_ID,
        'size': TEST_TOURNAMENT_SIZE,
        'status': persistence.AnytimeStatus.RECRUITING,
        'players': [{
            'user_id': TEST_USER_NAME,
            'user_name': TEST_USER_NAME,
            'decks': None
        }]
    })

    assert persistence.is_username_used(
        TEST_USER_NAME,
        TEST_SERVER_ID,
        TEST_TOURNAMENT_SIZE
    )
