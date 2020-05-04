import requests
import json
import os

from functools import partial
from typing import Union
from requests.auth import HTTPBasicAuth
from jirasession.user import JiraUser

class JiraSession(requests.Session):
    jirauser: JiraUser
    session: requests.Session
    base_url: str

    def __init__(self, username: str, token: str, server: str, session: requests.Session = None, max_retries: int = 3,
                 pool_connections: int = 16, pool_maxsize: int = 16, resolve_status_codes:list = [200, 201]):
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
        self.retries = max_retries
        self.resolve_status_codes = resolve_status_codes
        if 200 not in resolve_status_codes:
            self.resolve_status_codes.append(200)
        self.mount("https://", adapters)
        self.mount('http://', adapters)
        self.headers.update({"Accept": "application/json", "Content-Type": "application/json"})

        # attempt user login
        self.jirauser = JiraUser().login(username, token, server)
        self.auth = HTTPBasicAuth(self.jirauser.username, self.jirauser.token)

    def _resolver(self, request: partial) -> requests.Response:
        """attempt to resolve a bad requests
        don't call this method alone
        """
        attempt = 1
        resp = request()
        while attempt <= self.retries and resp.status_code not in self.resolve_status_codes:
            resp = request()
            attempt += 1
        return resp

    def link_issues(self, main_issue_key:str, sub_issue_key:str, relationship:str = 'relates to',
                    comment: dict = None) -> requests.Response:
        """link two issues together, in and out will relate to jira api route but has no effect on functionality
        
        main_issue_key {str} -- main issue key
        sub_issue_key {str} -- sub issue key to link with main
        relationship {str] -- type of link, default: Relates To
        comment {dict} [optional] -- comment for linking of issues
        
        return {requests.Response} -- response from issuelink route
        """
        #attempt to get sub issue
        resp = self.get_issue(sub_issue_key)
        if resp.status_code != 200:
            return resp
        sub_issue = resp.json()
        sub_issue_obj = {
            'object': {
                'summary': sub_issue.get('fields', {}).get('summary',
                                                           f'Linking {sub_issue_key!r}to {main_issue_key!r}'),
                'title': sub_issue_key,
                'url': sub_issue.get('self', f'{self.base_url}/issue/{sub_issue_key}'),
                'status': sub_issue.get('fields', {}).get('status', {})
            }
        }

        url = f'{self.base_url}/issue/{main_issue_key}/remoteLink'
        payload = {
            'relationship': relationship,
            'object': sub_issue_obj
        }
        if comment:
            payload.update({'comment': comment})
        return self._resolver(partial(self.post, url, data=json.dumps(payload)))

    def add_attachment(self, issue_key: str, filepath: str) -> requests.Response:
        """
        add an attachment to an issue

        issue_key {str} -- id or key of issue to add attachment
        filepath {str} -- path to file to use as attachment

        return {requests.Response} -- response from attachment route
        """
        url = f'{self.base_url}/issue/{issue_key}/attachments'
        if not os.path.exists(filepath):
            raise FileNotFoundError(f'Could not locate file at: {filepath}!r')
        if not os.path.isfile(filepath):
            raise TypeError(f'Could not open: {filepath!r}. Must be a file.')
        with open(filepath, 'rb') as fin:
            headers = {'Content-Type':None, 'X-Atlassian-Token': 'nocheck'}
            return self._resolver(partial(self.post, url, files={'file': fin}, headers=headers))

    def create_issue(self, content: dict) -> requests.Response:
        """
        create a new issue

        content {dict} -- dictionary of issue content

        return {requests.Response} -- response from post
        """
        url = f'{self.base_url}/issue'
        if 'fields' not in content:
            content = {'fields': content}
        return self._resolver(partial(self.post, url, data=json.dumps(content)))

    def get_issue(self, issue_key: str, fields:list = ['*all'], expand:dict = {}) -> requests.Response:
        """
        get jira issue by id

        issue_key {str} -- key of issue to get
        fields {list} -- fields to retrieve, add a '-' to a field to remove it. Default: *all
        expand {dict} -- custom expand for search, use jira api docs to further expand

        return {requests.Response} -- response from issue route (GET)
        """
        url = f'{self.base_url}/issue/{issue_key}'
        params = {'fields':fields}
        if expand:
            params.update({'expand': expand})
        return self._resolver(partial(url, self.get, params=params))

    def delete_issue(self, issue_key: str, delete_subtasks:bool=False) -> requests.Response:
        """
        delete and issue by id

        issue_key {str} -- key of issue to delete

        return {requests.Response} -- response from delete
        """
        url = f'{self.base_url}/issue/{issue_key}'
        return self._resolver(partial(self.delete, url, params={'deletesubtasks': delete_subtasks}))


    def update_issue(self, issue_key:str, content: dict) -> requests.Response:
        """
        update an issue by id

        issue_key {str} -- key of issue to update
        content {dict} -- dictionary of issue content

        return {requests.Response} -- response from put
        """
        url = f'{self.base_url}/issue/{issue_key}'
        if 'fields' not in content:
            content = {'fields': content}
        return self._resolver(partial(self.put, url, data=json.dumps(content)))


    def account_info(self) -> requests.Response:
        """
        get jira accountid from current auth creds

        return {int} -- accountid or None
        """
        url = f'{self.base_url}/myself'
        return self.get(url)

    def assign_issue(self, issue_key: str, accountid: str) -> requests.Response:
        """
        assign a issue to the current user accountid

        issue_key {str} -- newly created issue key
        """
        url = f'{self.base_url}/issue/{issue_key}/assignee'
        return self._resolver(partial(self.put, url, data=json.dumps({'accountId': accountid})))

    def get_transitions_from_issue(self, issue_key: str) -> requests.Response:
        """
        get the available transitions for a issue

        issue_key {str} -- issue key to pull available transitions from

        return {requests.Response} -- response from get to transitions route
        """
        url = f'{self.base_url}/issue/{issue_key}/transitions'
        return self._resolver(partial(self.get, url))

    def transition_issue(self, issue_key: str, transition_state_id: str) -> requests.Response:
        """
        transition a issue to a new state by id

        issue_key {str} -- issue key to pull available transitions from
        transition_state_id {str} -- new transition state id

        return {requests.Response} -- response from post to transitions route
        """
        url = f'{self.base_url}/issue/{issue_key}/transitions'
        return self._resolver(partial(self.post, url, data=json.dumps({'transition': {'id': transition_state_id}})))

    def add_comment(self, issue_key: str, comment: str) -> requests.Response:
        """
        add a new comment to a issue

        issue_key {str} -- issue key to pull available transitions from
        comment {str} -- string to add as comment

        return {requests.Response} -- response from post to comment route
        """
        url = f'{self.base_url}/issue/{issue_key}/comment'
        return self._resolver(partial(self.post, url, data=json.dumps({'body': comment})))

    def track_issue_time(self, issue_key:str, time_spent: str) -> requests.Response:
        """
        add time for time tracking application for a issue

        issue_key {str} -- issue key to pull available transitions from
        time_spent {str} -- jira format time. ex: 1d 2h 3m

        return {requests.Response} -- response from post to worklog route
        """
        url = f'{self.base_url}/issue/{issue_key}/worklog'
        return self._resolver(partial(self.post, url, data=json.dumps({'timeSpent': time_spent})))

    def get_jira_user(self, username: Union[str, list]) -> requests.Response:
        """
        get user information for jira users by usernames

        username {Union[str, list]} -- a username or list of usernames

        return {requests.Response} -- the response from the user bulk route
        """
        url = f'{self.base_url}/user/bulk?'
        if isinstance(username, str):
            url += f'username={username}'
        elif isinstance(username, list):
            url += f'username={"&username=".join(username)}'
        return self._resolver(partial(self.get, url))

    def assign_to_me(self, issue_key: str) -> requests.Response:
        """
        assign to yourself based on jirauser.userid
        issue {str} -- issue key to assign to yourself
        """
        return self.assign_issue(issue_key, self.jirauser.accountid)

    def get_comments(self, issue_key: str, start:int = 0, maxresults:int = 50, 
                     orderby:str = 'created', expand:bool = False) -> requests.Response:
        """get comments from an issue
        
        issue_key {str} -- issue key to get comments for
        start {int} -- start index for retrieval
        maxresults {int} -- max number of comments to retrieve [default: 50]
        orderby {str} -- order comments by created date, other options [-created, +created]
        expand {bool} -- if true, renderBody will be sent to get comments rendered in html

        return {requests.Response} -- response from comments route
        """
        url = f'{self.base_url}/issue/{issue_key}/comment'
        params = {'start': start, 'maxResults': maxresults, 'orderBy': orderby}
        if expand:
            params.update({'expand':'renderedBody'})
        return self._resolver(partial(self.get, url, params=params))

    def get_all_comments(self, issue_key: str, orderby:str = 'created', expand:bool = False) -> list:
        """get all comments from an issue

        issue_key {str} -- issue key to get comments for
        orderby {str} -- order comments by created date, other options [-created, +created]
        expand {bool} -- if true, renderBody will be sent to get comments rendered in html

        return {list} -- return list of comments from issue
        """
        issue_comments = []
        resp = self.get_comments(issue_key, orderby=orderby, expand=expand)
        if resp.status_code == 200:
            first_page = resp.json()
            total_comments = first_page.get('total', 0)
            issue_comments.extend(first_page.get('comments', []))
            for num_page in range(1, int(total_comments / 50)+1):
                resp = self.get_comments(issue_key, start=num_page*50, orderby=orderby, expand=expand)
                if resp.status_code == 200:
                    issue_comments.extend(resp.json().get('comments'), [])
        return issue_comments

    def get_project_issuetypes(self, project_key: str) -> list:
        """
        get the available issue types for a project

        project_key {str} -- key for project

        return {list} -- issuetypes found for the given project
        """
        url = f'{self.base_url}/project/{project_key}'
        resp = self.get(url)
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
        resp = self.get(url)
        priorities = []
        if resp.status_code == 200:
            for priority in resp.json():
                name = priority.get('name', '')
                if name:
                    priorities.append(name)
        return priorities


    def search(self, jql: str, start:int = 0, maxresults:int = 50, fields:list = ['*all'], validate:bool=True,
               validate_level:str = 'strict', expand:dict= {}) -> requests.Response:
        """
        search jira using a jql statement
        jql {str} -- jql string to search and validate if chosen
        start {int} -- start index
        maxresults {int} -- max number of results per page
        fields {list} -- fields to retrieve, add a '-' to a field to remove it. Default: *all
        validate {bool} -- to validate jql string upon search
        validate_level {str} -- validation level: strict, warn, none. Default: strict
        expand {dict} -- custom expand for search, use jira api docs to further expand

        return {requests.Response} -- response from search route (POST)
        """
        url = f'{self.base_url}/search'
        data = {
            'jql': jql,
            'startAt': start,
            'maxResults': maxresults,
            'fields': fields
        }
        if validate:
            data.update({'validateQuery': validate_level})
        if expand:
            data.update(expand)
        return self._resolver(partial(self.post, url, data=json.dumps(data)))

    def get_issues_from_project(self, project_key: str, maxresults: int = None) -> list:
        """
        retrieve all issues from a given project id
        project_key {str} -- project key, example: DEV
        maxresults {int} -- max number of results

        return {list} -- issues
        """
        issues = []
        jql = f'project={project_key}'
        resp = self.search(jql)
        if resp.status_code == 200:
            first_page = resp.json()
            total_issues = first_page.get('total', 0)
            issues.extend(first_page.get('issues', []))
            for num_page in range(1, int(total_issues / 50)+1):
                if maxresults and len(issues) >= maxresults:
                    return issues[:maxresults]
                resp = self.search(jql, start=num_page*50)
                if resp.status_code == 200:
                    issues.extend(resp.json().get('issues', []))
        return issues