import os
import random
import string
import allure
import requests

BASE_URL = "https://api.github.com"


def get_repositories_from_user(
    username: str,
    type: str = "owner",
    sort: str = "full_name",
    direction: str = None,
    per_page: int = 30,
    page: int = 1,
    include_token=True,
    random_token=False,
):
    """
    Lists public repositories for the specified user, paginated.

    Parameters:
    - username (str): The username of the GitHub account to fetch repositories for.
    - type (str): Filter repositories by type ('all', 'owner', 'member'). Default is 'owner'.
    - sort (str): Property to sort by ('created', 'updated', 'pushed', 'full_name'). Default is 'full_name'.
    - direction (str, optional): Sorting order ('asc', 'desc'). Default is 'asc' for 'full_name', otherwise 'desc'.
    - per_page (int): Number of results per page (max 100). Default is 30.
    - page (int): Page number for pagination. Default is 1.
    - include_token (bool): Whether to include a valid GitHub token in the request for authorization (default: True).
    - random_token (bool): Whether to generate a random token for testing purposes (default: False).

    Returns:
    - Response object containing the API response.
    """
    headers = {}

    # If include_token is True, fetch token from environment variable or generate a random token
    if include_token:
        if random_token:
            github_token = "".join(
                random.choices(string.ascii_letters + string.digits, k=40)
            )  # Random 40-character token
        else:
            github_token = os.getenv("GITHUB_TOKEN")

        if not github_token:
            raise ValueError("GITHUB_TOKEN is missing! Please set it in the .env file.")

        headers = {
            "Authorization": f"token {github_token}"
        }  # Add the token to the headers

    # Set the query parameters for the API request
    params = {"type": type, "sort": sort, "per_page": per_page, "page": page}

    # Handle sorting direction
    if direction:
        params["direction"] = direction
    elif sort == "full_name":
        params["direction"] = "asc"
    else:
        params["direction"] = "desc"

    # Send the GET request to the GitHub API
    url = f"{BASE_URL}/users/{username}/repos"
    response = requests.get(url, params=params, headers=headers)

    # Attach details of the API response to Allure
    allure.attach(
        str(response.status_code),
        name="Status Code",
        attachment_type=allure.attachment_type.TEXT,
    )
    allure.attach(
        response.text, name="Response Body", attachment_type=allure.attachment_type.JSON
    )

    return response


def get_repositories_from_logged_user(
    type: str = "all",  # Type filter for repositories (default: all)
    sort: str = "full_name",  # Sorting criteria (default: full_name)
    direction: str = None,  # Sorting order (default: asc for full_name)
    per_page: int = 30,  # Results per page (default: 30)
    page: int = 1,  # Page number (default: 1)
    visibility: str = None,  # Limit results to repositories with specified visibility
    affiliation: str = None,  # Filter repositories by affiliation (owner, collaborator, organization_member)
    include_token: bool = True,  # Whether to include the GitHub token for authentication (default: True)
    random_token: bool = False,  # Whether to generate a random token for testing (default: False)
    since: str = None,  # Show repositories updated after this time (ISO 8601 format)
    before: str = None,  # Show repositories updated before this time (ISO 8601 format)
):
    """
    Lists repositories for the logged-in user with optional filters for visibility, type, and more.

    Parameters:
    - type (str): Filter repositories by type ('all', 'owner', 'member'). Default is 'all'.
    - sort (str): Property to sort by ('created', 'updated', 'pushed', 'full_name'). Default is 'full_name'.
    - direction (str): Sorting order ('asc', 'desc'). Default is 'asc' for 'full_name', otherwise 'desc'.
    - per_page (int): Number of results per page. Default is 30.
    - page (int): Page number for pagination. Default is 1.
    - visibility (str): Filter by repository visibility ('all', 'public', 'private'). Default is 'all'.
    - affiliation (str): Filter repositories by affiliation ('owner', 'collaborator', 'organization_member'). Default is 'owner,collaborator,organization_member'.
    - include_token (bool): Whether to include a GitHub token in the request. Default is True.
    - random_token (bool): Whether to generate a random token for testing. Default is False.
    - since (str): Only show repositories updated after this time (ISO 8601 format).
    - before (str): Only show repositories updated before this time (ISO 8601 format).

    Returns:
    - Response object containing the API response.
    """
    headers = {}

    # If include_token is True, fetch token from environment variable or generate a random token
    if include_token:
        if random_token:
            github_token = "".join(
                random.choices(string.ascii_letters + string.digits, k=40)
            )  # Random 40-character token
        else:
            github_token = os.getenv("GITHUB_TOKEN")

        if not github_token:
            raise ValueError("GITHUB_TOKEN is missing! Please set it in the .env file.")

        headers = {"Authorization": f"token {github_token}"}  # Add token to the headers

    # Set the query parameters for the API request
    params = {
        "type": type,
        "sort": sort,
        "per_page": per_page,
        "page": page,
        "visibility": visibility,
        "affiliation": affiliation,
        "since": since,
        "before": before,
    }

    # Remove any None values from the params dictionary
    params = {key: value for key, value in params.items() if value is not None}

    # Handle sorting direction
    if direction:
        params["direction"] = direction
    elif sort == "full_name":
        params["direction"] = "asc"
    else:
        params["direction"] = "desc"

    # Send the GET request to the GitHub API
    url = f"{BASE_URL}/user/repos"
    response = requests.get(url, params=params, headers=headers)

    # Attach details of the API response to Allure for visibility
    allure.attach(
        str(response.status_code),
        name="Status Code",
        attachment_type=allure.attachment_type.TEXT,
    )
    allure.attach(
        response.text, name="Response Body", attachment_type=allure.attachment_type.JSON
    )

    return response


def get_commits_of_repository(
    owner: str,
    repo: str,
    sha: str = None,
    path: str = None,
    author: str = None,
    committer: str = None,
    since: str = None,
    until: str = None,
    per_page: int = 30,
    page: int = 1,
    include_token: bool = True,
    random_token: bool = False,
):
    """
    Fetches a list of commits for a given repository.

    Parameters:
    - owner (str): GitHub username of the repository owner.
    - repo (str): Name of the repository.
    - sha (str, optional): SHA or branch to start listing commits from. Default is the repository's default branch.
    - path (str, optional): Filter commits that modify a specific file or directory.
    - author (str, optional): Filter by commit author (GitHub username or email address).
    - committer (str, optional): Filter by commit committer (GitHub username or email address).
    - since (str, optional): Only show commits after this timestamp (ISO 8601 format).
    - until (str, optional): Only show commits before this timestamp (ISO 8601 format).
    - per_page (int, optional): Number of commits per page. Default is 30.
    - page (int, optional): Page number for pagination. Default is 1.
    - include_token (bool, optional): Whether to include a GitHub token for authentication (default: True).
    - random_token (bool, optional): Whether to generate a random token for testing (default: False).

    Returns:
    - Response object containing the API response with commit data.
    """
    headers = {}

    # If include_token is True, fetch token from environment variable or generate a random token
    if include_token:
        if random_token:
            github_token = "".join(
                random.choices(string.ascii_letters + string.digits, k=40)
            )  # Random 40-character token
        else:
            github_token = os.getenv("GITHUB_TOKEN")

        if not github_token:
            raise ValueError("GITHUB_TOKEN is missing! Please set it in the .env file.")

        headers["Authorization"] = f"Bearer {github_token}"  # Add token to the headers

    # Set query parameters for fetching commits, filtering out None values
    params = {
        "sha": sha,
        "path": path,
        "author": author,
        "committer": committer,
        "since": since,
        "until": until,
        "per_page": per_page,
        "page": page,
    }
    params = {key: value for key, value in params.items() if value is not None}

    # Construct the API endpoint URL for fetching commits
    url = f"{BASE_URL}/repos/{owner}/{repo}/commits"

    # Send the GET request to the GitHub API
    with allure.step(f"Sending GET request to fetch commits for {owner}/{repo}"):
        response = requests.get(url, params=params, headers=headers)

    # Attach response details to Allure for visibility
    with allure.step("Attach API response details to Allure"):
        allure.attach(
            str(response.status_code),
            name="Status Code",
            attachment_type=allure.attachment_type.TEXT,
        )
        allure.attach(
            response.text,
            name="Response Body",
            attachment_type=allure.attachment_type.JSON,
        )

    return response
