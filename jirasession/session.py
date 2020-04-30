import requests
import json

from typing import Union
from requests.auth import HTTPBasicAuth
from jirasession.user import JiraUser

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
        return self.get(url)

    def assign_issue(self, issue_id: str, accountid: str) -> requests.Response:
        """
        assign a issue to the current user accountid

        issue_id {str} -- newly created issue id
        """
        url = f'{self.base_url}/issue/{issue_id}/assignee'
        return self.put(url, data=json.dumps({'accountId': accountid}))

    def get_transitions_from_issue(self, issue_id: str) -> requests.Response:
        """
        get the available transitions for a issue

        issue_id {str} -- issue key to pull available transitions from

        return {requests.Response} -- response from get to transitions route
        """
        url = f'{self.base_url}/issue/{issue_id}/transitions'
        return self.get(url)

    def transition_issue(self, issue_id: str, transition_state_id: str) -> requests.Response:
        """
        transition a issue to a new state by id

        issue_id {str} -- issue key to pull available transitions from
        transition_state_id {str} -- new transition state id

        return {requests.Response} -- response from post to transitions route
        """
        url = f'{self.base_url}/issue/{issue_id}/transitions'
        return self.post(url, data=json.dumps({'transition': {'id': transition_state_id}}))

    def add_comment(self, issue_id: str, comment: str) -> requests.Response:
        """
        add a new comment to a issue

        issue_id {str} -- issue key to pull available transitions from
        comment {str} -- string to add as comment

        return {requests.Response} -- response from post to comment route
        """
        url = f'{self.base_url}/issue/{issue_id}/comment'
        return self.post(url, data=json.dumps({'body': comment}))

    def track_issue_time(self, issue_id:str, time_spent: str) -> requests.Response:
        """
        add time for time tracking application for a issue

        issue_id {str} -- issue key to pull available transitions from
        time_spent {str} -- jira format time. ex: 1d 2h 3m

        return {requests.Response} -- response from post to worklog route
        """
        url = f'{self.base_url}/issue/{issue_id}/worklog'
        return self.post(url, data=json.dumps({'timeSpent': time_spent}))

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
        return self.get(url)

    def assign_to_me(self, issue_id: str) -> requests.Response:
        """
        assign to yourself based on jirauser.userid
        issue {str} -- issue id to assign to yourself
        """
        return self.assign_issue(issue_id, self.jirauser.accountid)

    def get_comments(self, issue_id: str, start:int = 0, maxresults:int = 50, 
                     orderby:str = 'created', expand:bool = False) -> requests.Response:
        """get comments from an issue
        
        issue_id {str} -- issue id to get comments for
        start {int} -- start index for retrieval
        maxresults {int} -- max number of comments to retrieve [default: 50]
        orderby {str} -- order comments by created date, other options [-created, +created]
        expand {bool} -- if true, renderBody will be sent to get comments rendered in html

        return {requests.Response} -- response from comments route
        """
        url = f'{self.base_url}/issue/{issue_id}/comment'
        params = {'start': start, 'maxResults': maxresults, 'orderBy': orderby}
        if expand:
            params.update({'expand':'renderedBody'})
        return self.get(url, params=params)

    def get_all_comments(self, issue_id: str, orderby:str = 'created', expand:bool = False) -> list:
        """get all comments from an issue

        issue_id {str} -- issue id to get comments for
        orderby {str} -- order comments by created date, other options [-created, +created]
        expand {bool} -- if true, renderBody will be sent to get comments rendered in html

        return {list} -- return list of comments from issue
        """
        issue_comments = []
        resp = self.get_comments(issue_id, orderby=orderby, expand=expand)
        if resp.status_code == 200:
            first_page = resp.json()
            total_comments = first_page.get('total', 0)
            issue_comments.extend(first_page.get('comments', []))
            for num_page in range(1, int(total_comments / 50)+1):
                resp = self.get_comments(issue_id, start=num_page*50, orderby=orderby, expand=expand)
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
        return self.post(url, data=json.dumps(data))

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