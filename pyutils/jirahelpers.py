import os

import jira


def get_user_tickets(username, jira_api_token=os.getenv('JIRA_API_KEY')):
    """get_user_tickets
    Returns a list of tickets that the user is assigned to.
    """

    project_query = 'project = "DEV"'

    status_query = ('status in ("Backlog", "In Progress",'
                    '"Ready to Deploy", "Code Review", "Ready to Test", "To Do")')

    assignee_query = f'assignee = "{username}"'

    j = jira.JIRA("https://promoboxx.atlassian.net",
                  basic_auth=(username, jira_api_token))

    full_query = f'{project_query} AND {status_query} AND {assignee_query}'
    return j.search_issues(full_query)
