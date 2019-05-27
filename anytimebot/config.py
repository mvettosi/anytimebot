import json
import os

# Load configurations
CONFIG_FILE_NAME = 'config.json'
config_file_path = os.path.abspath(CONFIG_FILE_NAME)
with open(config_file_path) as config_file:
    data = json.load(config_file)

TOKEN = data['discord_token']
CHALLONGE_USERNAME = data['challonge_username']
CHALLONGE_API_KEY = data['challonge_api_key']
servers = data['servers']

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
