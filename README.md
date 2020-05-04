# Jirasession

    A light weight library to interact with the Jira API
    
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