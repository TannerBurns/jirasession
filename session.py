import requests
import json

from typing import Union
from requests.auth import HTTPBasicAuth
from user import JiraUser

class JiraSession(requests.Session):
    jirauser: JiraUser
    session: requests.Session
    base_url: str

    def __init__(self, username: str, token: str, server: str, session: requests.Session = None, max_retries: int = 3,
                 pool_connections: int = 16, pool_maxsize: int = 16, raise_exception: bool = True):
        super().__init__()

        # initialize session
        if session:
            self = session
        server = server if server[-1] != '/' else ''.join(server[:-1])
        self.base_url = f'{server}/rest/api/latest'
        adapters = requests.adapters.HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=max_retries
        )
        self.mount("https://", adapters)
        self.mount('http://', adapters)
        self.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
        self.raise_exception = raise_exception

        # attempt user login
        self.jirauser = JiraUser().login(username, token, server)
        self.auth = HTTPBasicAuth(self.jirauser.username, self.jirauser.token)


    def create_issue(self, content: dict) -> requests.Response:
        """
        create a new issue and assign it to the user who created it

        issue_content {str} -- raw json dump of issue data

        return {requests.Response} -- response from post
        """
        url = f'{self.base_url}/issue'
        return self.post(url, data=json.dumps(content))

    def account_info(self) -> requests.Response:
        """
        get jira accountid from current auth creds

        return {int} -- accountid or None
        """
        url = f'{self.base_url}/myself'
        return self.session.get(url)

    def assign_issue(self, issue_id: str, accountid: str) -> requests.Response:
        """
        assign a issue to the current user accountid

        issue_id {str} -- newly created issue id
        """
        url = f'{self.base_url}/issue/{issue_id}/assignee'
        return self.session.put(url, data=json.dumps({'accountId': accountid}))

    def get_transitions_from_issue(self, issue_id: str) -> requests.Response:
        """
        get the available transitions for a issue

        issue_id {str} -- issue key to pull available transitions from

        return {requests.Response} -- response from get to transitions route
        """
        url = f'{self.base_url}/issue/{issue_id}/transitions'
        return self.session.get(url)

    def transition_issue(self, issue_id: str, transition_state_id: str) -> requests.Response:
        """
        transition a issue to a new state by id

        issue_id {str} -- issue key to pull available transitions from
        transition_state_id {str} -- new transition state id

        return {requests.Response} -- response from post to transitions route
        """
        url = f'{self.base_url}/issue/{issue_id}/transitions'
        return self.session.post(url, data=json.dumps({'transition': {'id': transition_state_id}}))

    def add_comment(self, issue_id: str, comment: str) -> requests.Response:
        """
        add a new comment to a issue

        issue_id {str} -- issue key to pull available transitions from
        comment {str} -- string to add as comment

        return {requests.Response} -- response from post to comment route
        """
        url = f'{self.base_url}/issue/{issue_id}/comment'
        return self.session.post(url, data=json.dumps({'body': comment}))

    def track_issue_time(self, issue_id:str, time_spent: str) -> requests.Response:
        """
        add time for time tracking application for a issue

        issue_id {str} -- issue key to pull available transitions from
        time_spent {str} -- jira format time. ex: 1d 2h 3m

        return {requests.Response} -- response from post to worklog route
        """
        url = f'{self.base_url}/issue/{issue_id}/worklog'
        return self.session.post(url, data=json.dumps({'timeSpent': time_spent}))

    def get_jira_user(self, username: Union[str, list]) -> requests.Response:
        """
        get user infomration for jira users by usernames

        username {Union[str, list]} -- a username or list of usernames

        return {requests.Response} -- the response from the user bulk route
        """
        url = f'{self.base_url}/user/bulk?'
        if isinstance(username, str):
            url += f'username={username}'
        elif isinstance(username, list):
            url += f'username={"&username=".join(username)}'
        return self.session.get(url)

    def assign_to_me(self, issue: str):
        """
        assign to yourself based on jirauser.userid
        issue {str} -- issue id to assign to yourself
        """
        return self.assign_issue(issue, self.jirauser.accountid)

    def get_issues_from_project(self, id: int, maxresults: int = None) -> list:
        """
        retrieve all issues from a given project id
        id {int} -- id for project
        maxresults {int} -- max number of results

        !**THIS NEEDS TO BE UPDATED**

        return {list} -- issues
        """
        url = f'{self.base_url}/board/{id}/issue'
        resp = self.session.get(url, params={'maxResults': maxresults})
        issues = []
        if resp.status_code == 200:
            data = resp.json()
            issues.extend([i for i in data.get('issues', []) if i])
        return issues

    def get_project_issuetypes(self, project_key: str) -> list:
        """
        get the available issue types for a project

        project_key {str} -- key for project

        return {list} -- issuetypes found for the given project
        """
        url = f'{self.base_url}/project/{project_key}'
        resp = self.session.get(url)
        issuetypes = []
        if resp.status_code == 200:
            for issuetype in resp.json().get('issueTypes', []):
                name = issuetype.get('name', '')
                if name:
                    issuetypes.append(name)
        return issuetypes

    def jira_priorities_list(self) -> list:
        """
        get the available priorities for a project

        project_key {str} -- key for project

        return {list} -- priorities found for the given project
        """
        url = f'{self.base_url}/priority'
        resp = self.session.get(url)
        priorities = []
        if resp.status_code == 200:
            for priority in resp.json():
                name = priority.get('name', '')
                if name:
                    priorities.append(name)
        return priorities