import requests

class JiraUser(object):
    """An authenticated Jira user"""
    username: str
    token: str
    server: str
    accountid: str
    email: str
    timezone: str

    def __init__(self, username:str=None, token: str=None, server:str=None):
        """a JiraUser object that contains information for the authenticated user
        
        username {str} -- username for jira account
        token {str} -- api token for jira account
        server {str} -- server to build rest url from

        """
        self.username = username
        self.token = token
        if server:
            server = server if server[-1] != '/' else ''.join(server[:-1])
            self.base_url = f'{server}/rest/api/latest'


    @classmethod
    def login(cls, username:str=None, token: str=None, server:str=None) -> object:
        """ login to a jirasession
        
        username {str} -- username for jira account
        token {str} -- api token for jira account
        server {str} -- server to build rest url from

        return {JiraUser} -- returns a logged in user, the accountid, email and timezone have been set
        """
        newuser = cls(username=username, token=token, server=server)
        resp = newuser.account_information()
        assert (resp.status_code == 200), f'Unable to login as user:' \
                                          f' {newuser.username!r} with token: {newuser.token!r}.' \
                                          f' Status Code: {resp.status_code}, Error: {resp.text}'

        content = resp.json()
        newuser.accountid = content.get('accountId', '')
        newuser.email = content.get('emailAddress', '')
        newuser.timezone = content.get('timeZone', '')
        return newuser

    def account_information(self) -> requests.Response:
        """ get account information for jira account from username and token

        return {requests.Response} response from myself route
        """
        url = f'{self.base_url}/myself'
        return requests.get(url, headers={'Accept':'application/json'}, auth=(self.username, self.token))



