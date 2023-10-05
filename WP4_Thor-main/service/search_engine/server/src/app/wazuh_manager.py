#!/usr/bin/env python3

import json
import requests
import urllib3
from base64 import b64encode

# Disable insecure https warnings (for self-signed SSL certificates)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class WazuhManager:
    def __init__(self, host="localhost", port=55000, user="wazuh",
                 password="wazuh", protocol="https",
                 login_endpoint='security/user/authenticate'):
        ''' Set up necessary config options for WazuhManager, and also gets and sets a JWT for future requests. '''

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.protocol = protocol
        self.login_endpoint = login_endpoint

        self.api_base_path = f"{self.protocol}://{self.host}:{self.port}/"
        self.jwt = self._authenticate()

    def _authenticate(self):
        ''' Authenticates WazuhManager to Wazuh cluster and returns a JWT for future requests.'''

        login_url = f"{self.api_base_path}{self.login_endpoint}"
        basic_auth = f"{self.user}:{self.password}".encode()
        login_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {b64encode(basic_auth).decode()}'}

        response = requests.post(
            login_url, headers=login_headers, verify=False)
        token = json.loads(response.content.decode())['data']['token']
        return token

    def _cdb_to_set(self, cdb_str):
        ''' Takes a wazuh .cdb content file as str and returns a set containing the keys.'''

        cdb_set = set()
        for item in cdb_str.split(":\n"):
            cdb_set.add(item)
        return cdb_set

    def _set_to_cdb(self, cdb_set):
        ''' Takes a set containing keys and returns a wazuh .cdb content file as str.'''

        cdb_str = ""
        for item in cdb_set:
            if item != "":
                cdb_str += item + ":\n"
        return cdb_str

    def block_ip(self, ip):
        ''' 
        Takes an IP as an input, then proceeds to update blacklist-thor.cdb file 
        on Wazuh manager by adding the IP to the list. Also restarts the
        manager for changes to take effect.
        '''
        requests_headers = {'Content-Type': 'application/json',
                            'Authorization': f'Bearer {self.jwt}'}

        blacklist_raw = requests.get(
            f"{self.api_base_path}lists/files/blacklist-thor?raw=true",
            headers=requests_headers, verify=False).text

        blacklist_set = self._cdb_to_set(blacklist_raw)
        blacklist_set.add(ip)
        blacklist_modified = self._set_to_cdb(blacklist_set)

        requests_headers['Content-Type'] = 'application/octet-stream'
        put_response = requests.put(
            f"{self.api_base_path}lists/files/blacklist-thor?overwrite=true",
            headers=requests_headers, verify=False, data=blacklist_modified)

        restart_response = requests.put(
            f"{self.api_base_path}/manager/restart?wait_for_complete=false",
            headers=requests_headers, verify=False, data=blacklist_modified)

    def unblock_ip(self, ip):
        ''' 
        Takes an IP as an input, then proceeds to update blacklist-thor.cdb file 
        on Wazuh manager by removing the IP from the list. Also restarts the
        manager for changes to take effect.
        '''

        requests_headers = {'Content-Type': 'application/json',
                            'Authorization': f'Bearer {self.jwt}'}

        blacklist_raw = requests.get(
            f"{self.api_base_path}lists/files/blacklist-thor?raw=true",
            headers=requests_headers, verify=False).text

        blacklist_set = self._cdb_to_set(blacklist_raw)

        try:
            blacklist_set.remove(ip)
        except KeyError:
            raise KeyError(f"Specified IP ({ip}) is not on the blacklist!")

        blacklist_modified = self._set_to_cdb(blacklist_set)

        requests_headers['Content-Type'] = 'application/octet-stream'
        put_response = requests.put(
            f"{self.api_base_path}lists/files/blacklist-thor?overwrite=true",
            headers=requests_headers, verify=False, data=blacklist_modified)

        restart_response = requests.put(
            f"{self.api_base_path}/manager/restart?wait_for_complete=false",
            headers=requests_headers, verify=False, data=blacklist_modified)
