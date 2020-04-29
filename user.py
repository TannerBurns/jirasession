import requests

class JiraUser(object):
    username: str
    token: str
    server: str
    accountid: str
    email: str
    timezone: str

    def __init__(self, username:str=None, token: str=None, server:str=None):
        self.username = username
        self.token = token
        if server:
            server = server if server[-1] != '/' else ''.join(server[:-1])
            self.base_url = f'{server}/rest/api/latest'


    @classmethod
    def login(cls, username:str=None, token: str=None, server:str=None):
        newuser = cls(username=username, token=token, server=server)
        resp = newuser.get_myself()
        assert (resp.status_code == 200), f'Unable to login as user:' \
                                          f' {newuser.username!r} with token: {newuser.token!r}.' \
                                          f' Status Code: {resp.status_code}, Error: {resp.text}'

        content = resp.json()
        newuser.accountid = content.get('accountId', '')
        newuser.email = content.get('emailAddress', '')
        newuser.timezone = content.get('timeZone', '')
        return newuser

    def get_myself(self):
        url = f'{self.base_url}/myself'
        return requests.get(url, headers={'Accept':'application/json'}, auth=(self.username, self.token))



