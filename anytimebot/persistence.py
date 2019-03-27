import pprint

from tinydb import TinyDB, where

db = TinyDB('db.json')
'''
{
    doc_id: '...',
    server_name: 'Server Name',
    user_id: '...',
    tournamen_size: '4',
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
join_requests = db.table('join_requests')

'''
{
    doc_id: '...',
    server_name: 'Server Name',
    size: 4,
    players: [
        user_id: '...',
        decks: [
            {
                text: 'some description',
                url: 'image url'
            }
        ]
    ]
}
'''
anytimes = db.table('anytimes')


# APIs
def add_to_waiting_list(server_name, user_id, size):
    """
    Creates a request for the user to enter an anytime, listing him as awaiting decks for the provided
    Server and tournament size
    :param server_name: The name of the server from which the user used the command
    :param user_id: the discord ID of the user
    :param size: The number of players the tournament should reach before start
    :return: the id of this specific request
    """
    print('')
    print('')
    print(f'add_to_waiting_list({server_name}, {user_id}, {size})')
    print('join_requests before:')
    pprint.pprint(join_requests.all())

    # Remove previous (uncompleted) join requests by this user
    join_requests.remove((where('server_name') == server_name) & (where('user_id') == user_id))

    # Insert new request
    new_request = {
        'server_name': server_name,
        'user_id': user_id,
        'tournamen_size': size,
        'decks': []
    }
    request_id = join_requests.insert(new_request)

    print('')
    print('join_requests after:')
    pprint.pprint(join_requests.all())
    return request_id


def is_join_request_still_valid(request_id):
    """
    Checks if a join request is still the latest one performed by the user or not
    :param server_name: the name of the server the request was performed into
    :param user_id: the ID of the user that performed the request
    :param request_id: The id returned by a add_to_waiting_list call
    :return: True if it's still the lastest performed request, false otherwise
    """
    return join_requests.contains(doc_ids=[request_id])


def add_deck(request_id, description, urls):
    print('')
    print('')
    print(f'add_deck({request_id}, {description}, {urls})')
    print('join_requests before:')
    pprint.pprint(join_requests.all())

    request = join_requests.get(doc_id=request_id)
    request['decks'].append({'text': description, 'urls': urls})
    join_requests.update(request, doc_ids=[request_id])

    print('')
    print('join_requests after:')
    pprint.pprint(join_requests.all())


def submit(request_id):
    request = join_requests.get(doc_id=request_id)
    if request is not None:
        anytime = anytimes.get(
            (where('server_name') == request['server_name']) &
            (where('size') == request['tournament_size'])
        )
        new_player = {
            'user_id': request['user_id'],
            'decks': request['decks']
        }
        if anytime is None:
            # This user is creating a new anytime
            anytime = {
                'server_name': request['server_name'],
                'size': request['tournament_size'],
                'players': [new_player]
            }
            anytimes.insert(anytime)
        else:
            anytime['players'].append(new_player)
        return anytime
    else:
        print(f'The request id {request_id} is invalid! Nothing to submit here...')
        return None
