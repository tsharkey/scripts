import argparse
import json
import os
import sys
from datetime import datetime

from jira import JIRA

IN_PROGRESS_STATUSES = '"In Progress", "Code Review", "Ready to Test", "Ready to Deploy"'

def main(start_date, end_date, emails, reports):
  jira_client = get_jira_client()
  reports = reports.split(",")

  for report in reports:
    output = issue_factory(jira_client, report, start_date, end_date, emails)
    write_json(f"{report}.json", output)

  return

"""
jira functions
"""
def get_jira_client():
  api_key = os.getenv("JIRA_API_KEY")
  if not api_key:
    print("Error: JIRA_API_KEY environment variable not found.")
    sys.exit(1) 

  return JIRA(server="https://promoboxx.atlassian.net", basic_auth=("tom@promoboxx.com", api_key))

"""
report functions
"""
def get_completed_points(jira_client, start_date, end_date, assignees):
  completed_issues = get_completed_issues(jira_client, start_date, end_date, assignees)

  # count total points completed
  assignee_points = {}
  for issue in completed_issues:
    points = issue.fields.customfield_10105

    assignee = issue.fields.assignee.displayName
    if assignee in assignee_points:
      assignee_points[assignee] += points
    else:
      assignee_points[assignee] = points

  return assignee_points

def get_completed_issues(jira_client, start_date, end_date, assignees):
  jql = f"resolutiondate >= '{start_date}' AND resolutiondate <= '{end_date}' AND assignee in ({assignees})"
  completed_issues = jira_client.search_issues(jql, expand="changelog")

  return completed_issues

def get_issues_by_statuses(jira_client, statuses, assignees):
  jql = f"status in ({statuses}) AND assignee in ({assignees})"
  issues = jira_client.search_issues(jql)

  # count points by assignee per status type
  assignee_points = {}
  for issue in issues:
    points = issue.fields.customfield_10105
    status = issue.fields.status.name
    assignee = issue.fields.assignee.displayName

    if assignee in assignee_points:
      if status in assignee_points[assignee]:
        assignee_points[assignee][status] += points
      else:
        assignee_points[assignee][status] = points
    else:
      assignee_points[assignee] = { status: points }

  return assignee_points

def status_times(jira_client, start_date, end_date, assignees):
  issues_with_change_log = get_completed_issues(jira_client, start_date, end_date, assignees)
  ticket_transitions = {}

  # track number of times a ticket transitioned to each status and the total time spent in that status
  for issue in issues_with_change_log:
    ticket_transitions[issue.key] = {"ticket_name": issue.fields.summary, "assignee": issue.fields.assignee.displayName, "time_from_in_progress_to_done": 0, "last_transition_time": ""}
    for cl in issue.changelog.histories:
      for item in cl.items:
        if item.field == "status":
          created_time = datetime.strptime(cl.created, "%Y-%m-%dT%H:%M:%S.%f%z")

          if item.toString in ticket_transitions[issue.key]:
            last_transition_time = datetime.strptime(ticket_transitions[issue.key]["last_transition_time"], "%Y-%m-%dT%H:%M:%S.%f%z")
            ticket_transitions[issue.key][item.toString]["count"] += 1
            ticket_transitions[issue.key][item.toString]["time"] += round((created_time - last_transition_time).total_seconds() / 86400, 2) 
          else:
            issue_date_created = datetime.strptime(issue.fields.created, "%Y-%m-%dT%H:%M:%S.%f%z")
            ticket_transitions[issue.key][item.toString] = {
              "count": 1,
              "time": round((created_time - issue_date_created).total_seconds() / 86400, 2) 
            }
            
          ticket_transitions[issue.key]["last_transition_time"] = cl.created

  # aggregate total time spent on ticket
  # get In Progress time, Ready to Test time, Ready to Deploy time, Code Review time and add them together
  for ticket in ticket_transitions:
    total_time = 0
    total_time += ticket_transitions[ticket]["In Progress"]["time"] if "In Progress" in ticket_transitions[ticket] else 0
    total_time += ticket_transitions[ticket]["Ready to Test"]["time"] if "Ready to Test" in ticket_transitions[ticket] else 0
    total_time += ticket_transitions[ticket]["Ready to Deploy"]["time"] if "Ready to Deploy" in ticket_transitions[ticket] else 0
    total_time += ticket_transitions[ticket]["Code Review"]["time"] if "Code Review" in ticket_transitions[ticket] else 0

    ticket_transitions[ticket]["time_from_in_progress_to_done"] = total_time
    
  return ticket_transitions

"""
factory functions
"""

def issue_factory(jira_client, report_type, start_date, end_date, assignees):
  if report_type == "completed":
    return get_completed_points(jira_client, start_date, end_date, assignees)
  elif report_type == "in_progress":
    return get_issues_by_statuses(jira_client, IN_PROGRESS_STATUSES, assignees)
  elif report_type == "status_times":
    return status_times(jira_client, start_date, end_date, assignees)
  else:
    print("Error: Invalid report type")
    sys.exit(1)

"""
util
"""
def replace_at_symbol(emails):
  return emails.replace("@", "\\u0040")

def write_json(filename, dict): 
  with open(filename, "w") as outfile: 
    json.dump(dict, outfile)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Get Jira Points')
  parser.add_argument('--start_date', type=str, help='Start Date')
  parser.add_argument('--end_date', type=str, help='End Date')
  parser.add_argument('--emails', type=str, help='Emails')
  parser.add_argument("--reports", type=str, help="Generate reports")
  args = parser.parse_args()
  main(args.start_date, args.end_date, replace_at_symbol(args.emails), args.reports)
