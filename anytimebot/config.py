# Configurations
TOKEN = 'NTU5NTI1NDAzMjMyOTYwNTQy.D3mqiw.q8ahM64wbmTQfE9e2eEj8poTAfA'

CHALLONGE_USERNAME = 'Drackmord'
CHALLONGE_API_KEY = '5D1gXENxEETwbeNUfRqLjiKvFQ7hj5A87e7jVPa1'

servers = {
    'default': {
        'role': 'Ticket 1',
        'role_missing_message': 'You need the `Ticket 1` role in order to subscribe to a tournament. '
                                'Ask a mod, it\'s free!',
        'wait_for_decks_message': "You've been added to the waiting list! "
                                  "Please send your deck, extra deck and side deck as images "
                                  "or in-game urls and then use the !submit command to complete the registration"
    },
    'Duel Links Meta': {
        'role': 'Ticket 1',
        'role_missing_message': 'Hello! Thanks for your interest in DLM anytime tournaments! '
                                'Unfortunately you don\'t seem to have any meta ticket left, '
                                'please purchase some in #ticket-channel and try again.'
    }
}


# Public utilities


def get_server_config(server_name, field):
    result = None
    if server_name in servers:
        server_config = servers[server_name]
    else:
        server_config = servers['default']
    if field in server_config:
        result = server_config[field]
    return result


def has_ticket(server_name, user):
    result = True
    required_role = get_server_config(server_name, 'role')
    if required_role is not None:
        result = required_role in [role.name for role in user.roles]
    return result
