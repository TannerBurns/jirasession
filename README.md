# Jirasession

    A light weight library to interact with the Jira API

# Documentation

- [ jirasession ](#jirasession_795013728)
    - [ jirasession.session ](#jirasession.session_1132787740)
        - [ jirasession.session.JiraSession ](#jirasession.session.JiraSession_1618412180)
            - [ JiraSession.__init__ ](#JiraSession.__init___1145426498)
            - [ JiraSession._resolver ](#JiraSession._resolver_2136038425)
            - [ JiraSession.account_info ](#JiraSession.account_info_1923044947)
            - [ JiraSession.add_attachment ](#JiraSession.add_attachment_1287029100)
            - [ JiraSession.add_comment ](#JiraSession.add_comment_1916702821)
            - [ JiraSession.assign_issue ](#JiraSession.assign_issue_957746152)
            - [ JiraSession.assign_to_me ](#JiraSession.assign_to_me_54485273)
            - [ JiraSession.create_issue ](#JiraSession.create_issue_179072605)
            - [ JiraSession.delete_issue ](#JiraSession.delete_issue_754956445)
            - [ JiraSession.get_all_comments ](#JiraSession.get_all_comments_922948529)
            - [ JiraSession.get_comments ](#JiraSession.get_comments_1007969053)
            - [ JiraSession.get_issue ](#JiraSession.get_issue_761676875)
            - [ JiraSession.get_issues_from_project ](#JiraSession.get_issues_from_project_1468054426)
            - [ JiraSession.get_jira_user ](#JiraSession.get_jira_user_1899597935)
            - [ JiraSession.get_project_issuetypes ](#JiraSession.get_project_issuetypes_381779567)
            - [ JiraSession.get_transitions_from_issue ](#JiraSession.get_transitions_from_issue_2109347701)
            - [ JiraSession.jira_priorities_list ](#JiraSession.jira_priorities_list_1946031269)
            - [ JiraSession.link_issues ](#JiraSession.link_issues_4091800)
            - [ JiraSession.link_types ](#JiraSession.link_types_1719868372)
            - [ JiraSession.search ](#JiraSession.search_1997452673)
            - [ JiraSession.track_issue_time ](#JiraSession.track_issue_time_882503857)
            - [ JiraSession.transition_issue ](#JiraSession.transition_issue_1486462247)
            - [ JiraSession.update_issue ](#JiraSession.update_issue_206318917)
    - [ jirasession.user ](#jirasession.user_2131495399)
        - [ jirasession.user.JiraUser ](#jirasession.user.JiraUser_1841751606)
            - [ JiraUser.__init__ ](#JiraUser.__init___1201648800)
            - [ JiraUser.account_information ](#JiraUser.account_information_304870234)


<a name="jirasession_795013728"></a>
## jirasession

Documentation for the JiraSession and JiraUser objects

<a name="jirasession.session_1132787740"></a>
## jirasession.session

<a name="jirasession.session.JiraSession_1618412180"></a>
### jirasession.session.JiraSession(self, username: str, token: str, server: str, session: requests.sessions.Session = None, max_retries: int = 3, pool_connections: int = 16, pool_maxsize: int = 16, resolve_status_codes: list = [200, 201, 204])

JiraSession object can be imported from jirasession.session or from jirasession

<a name="JiraSession.__init___1145426498"></a>
#### `JiraSession.__init__(self, username: str, token: str, server: str, session: requests.sessions.Session = None, max_retries: int = 3, pool_connections: int = 16, pool_maxsize: int = 16, resolve_status_codes: list = [200, 201, 204])`

Initialization of JiraSession

<a name="JiraSession._resolver_2136038425"></a>
#### `JiraSession._resolver(self, request: functools.partial) -> requests.models.Response`

attempt to resolve a bad requests
        don't call this method alone
        
<a name="JiraSession.account_info_1923044947"></a>
#### `JiraSession.account_info(self) -> requests.models.Response`


        get jira accountid from current auth creds

        return {int} -- accountid or None
        

<a name="JiraSession.add_attachment_1287029100"></a>
#### `JiraSession.add_attachment(self, issue_key: str, filepath: str) -> requests.models.Response`


        add an attachment to an issue

        issue_key {str} -- id or key of issue to add attachment
        filepath {str} -- path to file to use as attachment

        return {requests.Response} -- response from attachment route
        

<a name="JiraSession.add_comment_1916702821"></a>
#### `JiraSession.add_comment(self, issue_key: str, comment: str) -> requests.models.Response`


        add a new comment to a issue

        issue_key {str} -- issue key to pull available transitions from
        comment {str} -- string to add as comment

        return {requests.Response} -- response from post to comment route
        

<a name="JiraSession.assign_issue_957746152"></a>
#### `JiraSession.assign_issue(self, issue_key: str, accountid: str) -> requests.models.Response`


        assign a issue to the current user accountid

        issue_key {str} -- newly created issue key
        

<a name="JiraSession.assign_to_me_54485273"></a>
#### `JiraSession.assign_to_me(self, issue_key: str) -> requests.models.Response`


        assign to yourself based on jirauser.userid
        issue {str} -- issue key to assign to yourself
        

<a name="JiraSession.create_issue_179072605"></a>
#### `JiraSession.create_issue(self, content: dict) -> requests.models.Response`


        create a new issue

        content {dict} -- dictionary of issue content

        return {requests.Response} -- response from post
        

<a name="JiraSession.delete_issue_754956445"></a>
#### `JiraSession.delete_issue(self, issue_key: str, delete_subtasks: bool = False) -> requests.models.Response`


        delete and issue by id

        issue_key {str} -- key of issue to delete

        return {requests.Response} -- response from delete
        

<a name="JiraSession.get_all_comments_922948529"></a>
#### `JiraSession.get_all_comments(self, issue_key: str, orderby: str = 'created', expand: bool = False) -> list`

get all comments from an issue

        issue_key {str} -- issue key to get comments for
        orderby {str} -- order comments by created date, other options [-created, +created]
        expand {bool} -- if true, renderBody will be sent to get comments rendered in html

        return {list} -- return list of comments from issue
        

<a name="JiraSession.get_comments_1007969053"></a>
#### `JiraSession.get_comments(self, issue_key: str, start: int = 0, maxresults: int = 50, orderby: str = 'created', expand: bool = False) -> requests.models.Response`

get comments from an issue
        
        issue_key {str} -- issue key to get comments for
        start {int} -- start index for retrieval
        maxresults {int} -- max number of comments to retrieve [default: 50]
        orderby {str} -- order comments by created date, other options [-created, +created]
        expand {bool} -- if true, renderBody will be sent to get comments rendered in html

        return {requests.Response} -- response from comments route
        

<a name="JiraSession.get_issue_761676875"></a>
#### `JiraSession.get_issue(self, issue_key: str, fields: list = ['*all'], expand: dict = {}) -> requests.models.Response`


        get jira issue by id

        issue_key {str} -- key of issue to get
        fields {list} -- fields to retrieve, add a '-' to a field to remove it. Default: *all
        expand {dict} -- custom expand for search, use jira api docs to further expand

        return {requests.Response} -- response from issue route (GET)
        

<a name="JiraSession.get_issues_from_project_1468054426"></a>
#### `JiraSession.get_issues_from_project(self, project_key: str, maxresults: int = None) -> list`


        retrieve all issues from a given project id
        project_key {str} -- project key, example: DEV
        maxresults {int} -- max number of results

        return {list} -- issues
        

<a name="JiraSession.get_jira_user_1899597935"></a>
#### `JiraSession.get_jira_user(self, username: Union[str, list]) -> requests.models.Response`


        get user information for jira users by usernames

        username {Union[str, list]} -- a username or list of usernames

        return {requests.Response} -- the response from the user bulk route
        

<a name="JiraSession.get_project_issuetypes_381779567"></a>
#### `JiraSession.get_project_issuetypes(self, project_key: str) -> list`


        get the available issue types for a project

        project_key {str} -- key for project

        return {list} -- issuetypes found for the given project
        

<a name="JiraSession.get_transitions_from_issue_2109347701"></a>
#### `JiraSession.get_transitions_from_issue(self, issue_key: str) -> requests.models.Response`


        get the available transitions for a issue

        issue_key {str} -- issue key to pull available transitions from

        return {requests.Response} -- response from get to transitions route
        

<a name="JiraSession.jira_priorities_list_1946031269"></a>
#### `JiraSession.jira_priorities_list(self) -> list`


        get the available priorities for a project

        project_key {str} -- key for project

        return {list} -- priorities found for the given project
        

<a name="JiraSession.link_issues_4091800"></a>
#### `JiraSession.link_issues(self, in_issue_key: str, out_issue_key: str, link_type: str = 'relates to', comment: dict = None) -> requests.models.Response`

link two issues together, in and out will relate to jira api route but has no effect on functionality
        
        in_issue_key {str} -- the issue to link from
        out_issue_key {str} -- the issue to link to
        link_type {str] -- type of link, default: Relates To
        comment {dict} [optional] -- comment for linking of issues
        
        return {requests.Response} -- response from issuelink route
        

<a name="JiraSession.link_types_1719868372"></a>
#### `JiraSession.link_types(self) -> requests.models.Response`


        retrieve the link types for jira issues

        return {requests.Response} -- response from issueLinkType route
        

<a name="JiraSession.search_1997452673"></a>
#### `JiraSession.search(self, jql: str, start: int = 0, maxresults: int = 50, fields: list = ['*all'], validate: bool = True, validate_level: str = 'strict', expand: dict = {}) -> requests.models.Response`


        search jira using a jql statement
        jql {str} -- jql string to search and validate if chosen
        start {int} -- start index
        maxresults {int} -- max number of results per page
        fields {list} -- fields to retrieve, add a '-' to a field to remove it. Default: *all
        validate {bool} -- to validate jql string upon search
        validate_level {str} -- validation level: strict, warn, none. Default: strict
        expand {dict} -- custom expand for search, use jira api docs to further expand

        return {requests.Response} -- response from search route (POST)
        

<a name="JiraSession.track_issue_time_882503857"></a>
#### `JiraSession.track_issue_time(self, issue_key: str, time_spent: str) -> requests.models.Response`


        add time for time tracking application for a issue

        issue_key {str} -- issue key to pull available transitions from
        time_spent {str} -- jira format time. ex: 1d 2h 3m

        return {requests.Response} -- response from post to worklog route
        

<a name="JiraSession.transition_issue_1486462247"></a>
#### `JiraSession.transition_issue(self, issue_key: str, transition_state_id: str) -> requests.models.Response`


        transition a issue to a new state by id

        issue_key {str} -- issue key to pull available transitions from
        transition_state_id {str} -- new transition state id

        return {requests.Response} -- response from post to transitions route
        

<a name="JiraSession.update_issue_206318917"></a>
#### `JiraSession.update_issue(self, issue_key: str, content: dict) -> requests.models.Response`


        update an issue by id

        issue_key {str} -- key of issue to update
        content {dict} -- dictionary of issue content

        return {requests.Response} -- response from put
        

<a name="jirasession.user_2131495399"></a>
## jirasession.user

<a name="jirasession.user.JiraUser_1841751606"></a>
### jirasession.user.JiraUser(self, username: str = None, token: str = None, server: str = None)

An authenticated Jira user

<a name="JiraUser.__init___1201648800"></a>
#### `JiraUser.__init__(self, username: str = None, token: str = None, server: str = None)`

a JiraUser object that contains information for the authenticated user
        
        username {str} -- username for jira account
        token {str} -- api token for jira account
        server {str} -- server to build rest url from

        

<a name="JiraUser.account_information_304870234"></a>
#### `JiraUser.account_information(self) -> requests.models.Response`

 get account information for jira account from username and token

        return {requests.Response} response from myself route
        


    
# Basic example

```python
from jirasession import JiraSession

session = JiraSession('email', 'token', 'https://server.atlassian.net/')

new_isssue = {
    'project': {'key': 'DEV'},
    'summary': 'test',
    'description': 'test',
    'issuetype': {'name':'Ticket'}
}

resp = session.create_issue(new_isssue)
if resp.status_code == 200:
    print('issue created') # handle requests.Response to get issue information
else:
    print('error creating issue') # debug requests.Response here
```