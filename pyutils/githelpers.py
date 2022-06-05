import os
import re
import sys

from git import Repo
from termcolor import colored


def has_changes(repo=Repo(".")):
    """has_changes
    Returns True if there are uncommited changes in the repo.
    """

    return repo.is_dirty(untracked_files=True)


def is_on_default(remote, local=Repo(".")):
    """is_on_default
    Returns True if the active local branch is the default branch of the remote.
    """

    return local.active_branch.name == remote.default_branch


# TODO this needs to check against the default branch of the remote
def needs_pull(repo=Repo(".")):
    """needs_pull
    Returns True if the local repo is behind the remote.
    """

    repo_status = repo.git.status(porcelain="v2", branch=True)
    behind_match = re.search(r"#\sbranch\.ab\s\+(\d+)\s-(\d+)", repo_status)
    return behind_match and behind_match.group(2) != "0"

# TODO this needs to check against the default branch of the remote


def needs_push(repo=Repo(".")):
    """needs_push
    Returns True if the local repo is ahead of the remote.
    """

    repo_status = repo.git.status(porcelain="v2", branch=True)
    ahead_match = re.search(r"#\sbranch\.ab\s\+(\d+)\s-(\d+)", repo_status)
    return ahead_match and ahead_match.group(1) != "0"


def get_repo_full_name(repo=Repo(".")):
    """get_repo_full_name
    Returns the full name of the repo.
    ex: tsharkey/scripts
    """

    return repo.remotes.origin.url.split('.git')[0].split(':')[-1]


def get_branch_ticket_number(branch_name=Repo(".").active_branch.name):
    """get_branch_ticket_number
    Parses the ticket number from the branch name
    if there isn't one then it returns an empty string.
    """

    splits = branch_name.split('.')
    if len(splits) > 1:
        return splits[0]+": "
    return ""


def get_access_token():
    """get_access_token
    Gets a github access token from an environment variable
    """

    gat = os.getenv('GH_ACCESS_TOKEN')
    if not gat:
        print(colored("GH_ACCESS_TOKEN not set", "red"))
        sys.exit(1)
    return gat
