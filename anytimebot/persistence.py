from tinydb import TinyDB, Query

db = TinyDB('db.json')

'''
{
    name: 'server name',
    waiting: [
        {
            user: 'user name',
            size: <tournament size>
        },
        {
            user: 'user name 2',
            size: <tournament size>
        }
    ],
    anytimes: [
        {
            channel: 'channel id',
            challonge_id: 'challonge id',
            players: [
                'player1', 'player2', 'player3', 'player4'
            ]
        }
    ]
},
{
    ...
}
'''


def add_to_waiting_list(server_name, user_id, size):
    server = db.get(Query().name == server_name)
    print('')
    print(f'add_to_waiting_list({server_name}, {user_id}, {size})')
    print(f'DEBUG Server before: {server}')
    if server is not None:
        # Search and remove occurrences of the given user from the waiting list
        server['waiting'] = [user for user in server['waiting'] if user.get('id', None) != user_id]
    else:
        server = {'name': server_name, 'waiting': [], 'anytimes': []}
        db.insert(server)
    server['waiting'].append({'id': user_id, 'size': size})
    db.update(server, Query().name == server_name)
    print(f'DEBUG Server after: {server}')
