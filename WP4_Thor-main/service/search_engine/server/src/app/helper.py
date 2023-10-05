
import json


def get_wazuh_config():
    with open('wazuh-config.json') as config_file:
        config_data = json.load(config_file)
    server = config_data["server"]
    username = config_data["username"]
    password = config_data["password"]
    return server, username, password

def set_wazuh_config(server, username, password):
    try:
        new_config = {
            "server": server,
            "username": username,
            "password": password
        }
        with open('wazuh-config.json', 'w') as config_file:
            json.dump(new_config, config_file, indent=4)
    except Exception as e:
        print(e)
