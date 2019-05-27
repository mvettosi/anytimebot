from enum import IntEnum
from pprint import pprint
import sys

from tinydb import TinyDB, where, Query


DB_FILE = 'db.json'
this = sys.modules[__name__]


def init():
    this.db = TinyDB(DB_FILE)
    '''
    {
        doc_id: '...',
        server_id: '...',
        user_id: '...',
        tournament_size: '4',
        decks: [
            {
                text: 'some description',
                urls: [
                    'image url'
                ]
            }
        ]
    }
    '''
    this.join_requests = this.db.table('join_requests')

    '''
    {
        doc_id: 123,
        tournament_id: 123,
        server_id: '...',
        size: 4,
        status: AnytimeStatus
        players: [
            user_id: '...',
            user_name: '...',
            decks: [
                {
                    text: 'some description',
                    url: 'image url'
                }
            ]
        ]
    }
    '''
    this.anytimes = this.db.table('anytimes')


init()


class AnytimeStatus(IntEnum):
    RECRUITING = 1
    RUNNING = 2
    COMPLETED = 3


# APIs
def is_username_used(user_name, server_id, tournament_size):
    anytime = Query()
    player = Query()
    return anytimes.contains(
        (anytime.server_id == server_id) &
        (anytime.size == tournament_size) &
        (anytime.status == AnytimeStatus.RECRUITING) &
        (anytime.players.any(
            player.user_name == user_name
        ))
    )


def add_to_waiting_list(server_id, user, size):
    """
    Creates a request for the user to enter an anytime, listing him as awaiting decks for the provided
    Server and tournament size
    :param server_id: The name of the server from which the user used the command
    :param user_id: the discord ID of the user
    :param size: The number of players the tournament should reach before start
    :return: the id of this specific request
    """
    # Remove previous (uncompleted) join requests by this user
    join_requests.remove((where('server_id') == server_id) &
                         (where('user_id') == user.id))

    # Insert new request
    new_request = {
        'server_id': server_id,
        'user_id': user.id,
        'user_name': user.name,
        'tournament_size': size,
        'decks': []
    }
    request_id = join_requests.insert(new_request)

    return request_id


def is_join_request_still_valid(request_id):
    """
    Checks if a join request is still the latest one performed by the user or not
    :param server_id: the name of the server the request was performed into
    :param user_id: the ID of the user that performed the request
    :param request_id: The id returned by a add_to_waiting_list call
    :return: True if it's still the lastest performed request, false otherwise
    """
    return join_requests.contains(doc_ids=[request_id])


def add_deck(request_id, description, urls):
    request = join_requests.get(doc_id=request_id)
    request['decks'].append({'text': description, 'urls': urls})
    join_requests.update(request, doc_ids=[request_id])
    return request


def submit(request_id):
    request = join_requests.get(doc_id=request_id)
    if request is not None:
        anytime = anytimes.get(
            (where('server_id') == request['server_id']) &
            (where('size') == request['tournament_size']) &
            (where('status') == AnytimeStatus.RECRUITING)
        )
        new_player = {
            'user_id': request['user_id'],
            'user_name': request['user_name'],
            'decks': request['decks']
        }
        if anytime is None:
            # This user is creating a new anytime
            anytime_id = anytimes.insert({
                'server_id': request['server_id'],
                'size': request['tournament_size'],
                'status': AnytimeStatus.RECRUITING,
                'players': [new_player]
            })
            anytime = anytimes.get(doc_id=anytime_id)
        else:
            anytime['players'].append(new_player)
            anytimes.update(anytime, doc_ids=[anytime.doc_id])
        join_requests.remove(doc_ids=[request_id])
        return anytime
    else:
        print(
            f'The request id {request_id} is invalid! Nothing to submit here...')
        return None


def tournament_started(anytime_id, tournament_id):
    try:
        anytimes.update({'tournament_id': tournament_id,
                         'status': AnytimeStatus.RUNNING}, doc_ids=[anytime_id])
    except KeyError:
        print(
            f'Could not mark tournament with id={anytime_id} as started: tournament id not found!!')
        return None
    else:
        return anytimes.get(doc_id=anytime_id)


def add_channel_id(channel_id, anytime_id):
    try:
        anytimes.update({'channel_id': channel_id}, doc_ids=[anytime_id])
    except KeyError:
        print(
            f'Could not add channel to tournament with id={anytime_id}: tournament id not found!!')
        return None
    else:
        return anytimes.get(doc_id=anytime_id)


def remove_player(anytime_id, player_id):
    anytime = anytimes.get(doc_id=anytime_id)
    if anytime is not None:
        anytime['players'] = [player for player in anytime['players']
                              if player['user_id'] != player_id]
        anytimes.update(anytime, doc_ids=[anytime_id])
        return anytimes.get(doc_id=anytime_id)
    else:
        print(f'The provied anytime with id={anytime_id} was not found!')


def get_anytime(anytime_id):
    return anytimes.get(doc_id=anytime_id)
