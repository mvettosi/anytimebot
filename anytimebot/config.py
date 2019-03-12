# Configurations
TOKEN = 'NTIyMTA3MzcyODMxODk5NjQ5.DvGKPg.VdNfFHyTm76G6XgFaT9dl8rmxKc'

servers = {
    'default': {
        'role': 'Ticket1',
        'role_missing_message': 'You need the Ticket1 role in order to subscribe to a tournament. Ask a mod, it\'s free!',
        'wait_for_decks_message': "You've been added to the waiting list! Please your deck, extra deck and side deck as images or in-game urls and then use the !submit command to complete the registration"
    },
    'Duel Links Meta': {
        'role': 'Ticket1',
        'role_missing_message': 'Hello! Thanks for your interest in DLM anytime tournaments! Unfortunately you don\'t seem to have any meta ticket left, please purchase some in #ticket-channel and try again.'
    }
}


# Public utilities


def get_server_config(server, field):
    result = None
    if server in servers:
        server_config = servers[server]
    else:
        server_config = servers['default']
    if field in server_config:
        result = server_config[field]
    return result


def misses_role(server, user):
    result = False
    required_role = get_server_config(server, 'role')
    if required_role:
        result = required_role not in [role.name for role in user.roles]
    return result
