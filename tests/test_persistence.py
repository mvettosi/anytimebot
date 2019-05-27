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
    assert check_is_username_used()


def test_is_username_used_wrong_server_id():
    assert not check_is_username_used(server_id=TEST_SERVER_ID + 'a')


def test_is_username_used_wrong_size():
    assert not check_is_username_used(size=TEST_TOURNAMENT_SIZE + 1)


def test_is_username_used_running_status():
    assert not check_is_username_used(status=persistence.AnytimeStatus.RUNNING)


def test_is_username_used_completed_status():
    assert not check_is_username_used(
        status=persistence.AnytimeStatus.COMPLETED)


def test_is_username_used_wrong_name():
    assert not check_is_username_used(user_name=TEST_USER_NAME + 'a')


def test_is_username_used_wrong_user_id():
    assert check_is_username_used(user_id=TEST_USER_NAME + 'a')


def test_add_to_waiting_list_empty_db():
    persistence.add_to_waiting_list(
        TEST_SERVER_ID,
        MockUser(
            name=TEST_USER_NAME,
            id=TEST_USER_NAME
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


def test_add_to_waiting_list_previous_req_same_server():
    persistence.join_requests.insert({
        'server_id': TEST_SERVER_ID,
        'user_id': TEST_USER_NAME,
        'user_name': TEST_USER_NAME,
        'tournament_size': TEST_TOURNAMENT_SIZE,
        'decks': ['trash']
    })

    persistence.add_to_waiting_list(
        TEST_SERVER_ID,
        MockUser(
            name=TEST_USER_NAME,
            id=TEST_USER_NAME
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


def test_add_to_waiting_list_previous_req_diff_server():
    persistence.join_requests.insert({
        'server_id': TEST_SERVER_ID + 'a',
        'user_id': TEST_USER_NAME,
        'user_name': TEST_USER_NAME,
        'tournament_size': TEST_TOURNAMENT_SIZE,
        'decks': ['trash']
    })

    persistence.add_to_waiting_list(
        TEST_SERVER_ID,
        MockUser(
            name=TEST_USER_NAME,
            id=TEST_USER_NAME
        ),
        TEST_TOURNAMENT_SIZE
    )

    all_requests = persistence.join_requests.all()
    assert len(all_requests) == 2


def test_is_join_request_still_valid_true():
    request_id = persistence.add_to_waiting_list(
        TEST_SERVER_ID,
        MockUser(
            name=TEST_USER_NAME,
            id=TEST_USER_NAME
        ),
        TEST_TOURNAMENT_SIZE
    )

    assert persistence.is_join_request_still_valid(request_id)


def test_is_join_request_still_valid_false():
    request_id = persistence.add_to_waiting_list(
        TEST_SERVER_ID,
        MockUser(
            name=TEST_USER_NAME,
            id=TEST_USER_NAME
        ),
        TEST_TOURNAMENT_SIZE
    )

    request_id2 = persistence.add_to_waiting_list(
        TEST_SERVER_ID,
        MockUser(
            name=TEST_USER_NAME,
            id=TEST_USER_NAME
        ),
        TEST_TOURNAMENT_SIZE
    )

    assert not persistence.is_join_request_still_valid(request_id)
    assert persistence.is_join_request_still_valid(request_id2)


TEST_DECK_DESCRIPTION = "main deck"
TEST_DECK_URL = "https://media.discordapp.net/attachments/501380564486455307/574689873139859456/image0.png?width=694&height=926"


def test_add_deck():
    request_id = persistence.add_to_waiting_list(
        TEST_SERVER_ID,
        MockUser(
            name=TEST_USER_NAME,
            id=TEST_USER_NAME
        ),
        TEST_TOURNAMENT_SIZE
    )
    request = persistence.join_requests.get(doc_id=request_id)
    assert len(request['decks']) == 0

    persistence.add_deck(request_id, TEST_DECK_DESCRIPTION, TEST_DECK_URL)
    request = persistence.join_requests.get(doc_id=request_id)
    assert len(request['decks']) == 1


def test_submit_no_anytimes():
    request_id = persistence.add_to_waiting_list(
        TEST_SERVER_ID,
        MockUser(
            name=TEST_USER_NAME,
            id=TEST_USER_NAME
        ),
        TEST_TOURNAMENT_SIZE
    )
    persistence.add_deck(request_id, TEST_DECK_DESCRIPTION, [TEST_DECK_URL])

    anytime = persistence.submit(request_id)

    assert len(persistence.join_requests.all()) == 0
    assert len(persistence.anytimes.all()) == 1
    assert anytime['server_id'] == TEST_SERVER_ID
    assert anytime['size'] == TEST_TOURNAMENT_SIZE
    assert anytime['status'] == persistence.AnytimeStatus.RECRUITING
    assert len(anytime['players']) == 1
    player = anytime['players'][0]
    assert player['user_id'] == TEST_USER_NAME
    assert player['user_name'] == TEST_USER_NAME
    assert len(player['decks']) == 1
    deck = player['decks'][0]
    assert deck['text'] == TEST_DECK_DESCRIPTION
    assert len(deck['urls']) == 1
    assert deck['urls'][0] == TEST_DECK_URL


def test_submit_no_request():
    assert persistence.submit('random string') is None


def test_submit_existing_anytime():
    req1 = persistence.add_to_waiting_list(
        TEST_SERVER_ID,
        MockUser(
            name=TEST_USER_NAME + '1',
            id=TEST_USER_NAME + '1'
        ),
        TEST_TOURNAMENT_SIZE
    )
    persistence.add_deck(req1, TEST_DECK_DESCRIPTION, [TEST_DECK_URL])
    persistence.submit(req1)

    req2 = persistence.add_to_waiting_list(
        TEST_SERVER_ID,
        MockUser(
            name=TEST_USER_NAME + '2',
            id=TEST_USER_NAME + '2'
        ),
        TEST_TOURNAMENT_SIZE
    )
    persistence.add_deck(req2, TEST_DECK_DESCRIPTION, [TEST_DECK_URL])
    anytime = persistence.submit(req2)

    assert len(persistence.join_requests.all()) == 0
    assert len(persistence.anytimes.all()) == 1
    assert len(anytime['players']) == 2
    player1 = anytime['players'][0]
    player2 = anytime['players'][1]
    assert player1['user_name'] == TEST_USER_NAME + '1'
    assert player2['user_name'] == TEST_USER_NAME + '2'


TEST_TOURNAMENT_ID = 'test tournament id'


def test_tournament_started_happy_path():
    request_id = persistence.add_to_waiting_list(
        TEST_SERVER_ID,
        MockUser(
            name=TEST_USER_NAME,
            id=TEST_USER_NAME
        ),
        TEST_TOURNAMENT_SIZE
    )
    persistence.add_deck(request_id, TEST_DECK_DESCRIPTION, [TEST_DECK_URL])
    anytime = persistence.submit(request_id)

    started_anytime = persistence.tournament_started(
        anytime.doc_id, TEST_TOURNAMENT_ID)

    assert started_anytime is not None
    assert started_anytime['status'] == persistence.AnytimeStatus.RUNNING
    assert started_anytime['tournament_id'] == TEST_TOURNAMENT_ID


def test_tournament_started_missing_anytime():
    started_anytime = persistence.tournament_started(
        'random-id', TEST_TOURNAMENT_ID)

    assert started_anytime is None


TEST_CHANNEL_ID = 'channel_id'


def test_add_channel_id_happy_path():
    request_id = persistence.add_to_waiting_list(
        TEST_SERVER_ID,
        MockUser(
            name=TEST_USER_NAME,
            id=TEST_USER_NAME
        ),
        TEST_TOURNAMENT_SIZE
    )
    persistence.add_deck(request_id, TEST_DECK_DESCRIPTION, [TEST_DECK_URL])
    anytime = persistence.submit(request_id)

    updated_anytime = persistence.add_channel_id(
        TEST_CHANNEL_ID, anytime.doc_id)

    assert updated_anytime is not None
    assert updated_anytime['channel_id'] == TEST_CHANNEL_ID


def test_add_channel_id_missing_anytime():
    anytime = persistence.add_channel_id(TEST_CHANNEL_ID, "random-id")

    assert anytime is None


def test_remove_player_happy_path():
    req1 = persistence.add_to_waiting_list(
        TEST_SERVER_ID,
        MockUser(
            name=TEST_USER_NAME + '1',
            id=TEST_USER_NAME + '1'
        ),
        TEST_TOURNAMENT_SIZE
    )
    persistence.add_deck(req1, TEST_DECK_DESCRIPTION, [TEST_DECK_URL])
    persistence.submit(req1)
    req2 = persistence.add_to_waiting_list(
        TEST_SERVER_ID,
        MockUser(
            name=TEST_USER_NAME + '2',
            id=TEST_USER_NAME + '2'
        ),
        TEST_TOURNAMENT_SIZE
    )
    persistence.add_deck(req2, TEST_DECK_DESCRIPTION, [TEST_DECK_URL])
    anytime = persistence.submit(req2)

    anytime = persistence.remove_player(anytime.doc_id, TEST_USER_NAME + '1')

    assert len(anytime['players']) == 1
    player = anytime['players'][0]
    assert player['user_id'] == TEST_USER_NAME + '2'


def test_remove_player_missing_anytime():
    anytime = persistence.remove_player('random-id', TEST_USER_NAME)
    assert anytime is None


def test_remove_player_missing_player():
    request_id = persistence.add_to_waiting_list(
        TEST_SERVER_ID,
        MockUser(
            name=TEST_USER_NAME,
            id=TEST_USER_NAME
        ),
        TEST_TOURNAMENT_SIZE
    )
    persistence.add_deck(request_id, TEST_DECK_DESCRIPTION, [TEST_DECK_URL])
    anytime = persistence.submit(request_id)

    anytime = persistence.remove_player(anytime.doc_id, TEST_USER_NAME + '2')

    assert len(anytime['players']) == 1
    player = anytime['players'][0]
    assert player['user_id'] == TEST_USER_NAME


# Helper functions


def check_is_username_used(
        server_id=TEST_SERVER_ID,
        size=TEST_TOURNAMENT_SIZE,
        status=persistence.AnytimeStatus.RECRUITING,
        user_name=TEST_USER_NAME,
        user_id=TEST_USER_NAME):
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
