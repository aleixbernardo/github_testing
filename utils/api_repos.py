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

    Optional Query Parameters:
    - type: Filter repositories by type ('all', 'owner', 'member'). Default is 'owner'.
    - sort: Property to sort by ('created', 'updated', 'pushed', 'full_name'). Default is 'full_name'.
    - direction: Sorting order ('asc', 'desc'). Default is 'asc' for 'full_name', otherwise 'desc'.
    - per_page: Number of results per page (max 100). Default is 30.
    - page: Page number for pagination. Default is 1.
    """
    headers = {}
    if include_token:
        if random_token:
            # Generate a random token for testing purposes (e.g., a random string of 40 characters)
            github_token = "".join(
                random.choices(string.ascii_letters + string.digits, k=40)
            )
        else:
            # Retrieve token from environment variables
            github_token = os.getenv("GITHUB_TOKEN")

        if not github_token:
            raise ValueError("GITHUB_TOKEN is missing! Please set it in the .env file.")

        headers = {"Authorization": f"token {github_token}"}

    params = {"type": type, "sort": sort, "per_page": per_page, "page": page}

    if direction:
        params["direction"] = direction
    elif sort == "full_name":
        params["direction"] = "asc"
    else:
        params["direction"] = "desc"

    url = f"{BASE_URL}/users/{username}/repos"
    response = requests.get(url, params=params, headers=headers)
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
    visibility: str = None,
    affiliation: str = None,
    # Affiliation filter (default: owner,collaborator,organization_member)
    include_token: bool = True,  # Include GitHub token in the request
    random_token: bool = False,  # Whether to generate a random token for testing
    since: str = None,
    # Only show repositories updated after the given time (ISO 8601 format)
    before: str = None,
    # Only show repositories updated before the given time (ISO 8601 format)
):
    """
    Lists public repositories for the specified user, paginated with enhanced filters.

    Query Parameters:
    - visibility: Limit results to repositories with the specified visibility ('all', 'public', 'private'). Default is 'all'.
    - affiliation: Filter repositories by type ('owner', 'collaborator', 'organization_member'). Default is 'owner,collaborator,organization_member'.
    - type: Limit results to repositories of the specified type ('all', 'owner', 'public', 'private', 'member'). Default is 'all'.
    - sort: Property to sort by ('created', 'updated', 'pushed', 'full_name'). Default is 'full_name'.
    - direction: Sorting order ('asc', 'desc'). Default is 'asc' when sorting by 'full_name', otherwise 'desc'.
    - per_page: Number of results per page (max 100). Default is 30.
    - page: Page number for pagination. Default is 1.
    - since: Show repositories updated after the given time (ISO 8601 format).
    - before: Show repositories updated before the given time (ISO 8601 format).
    """

    # Set headers if token is included
    headers = {}
    if include_token:
        if random_token:
            # Generate a random token for testing purposes (e.g., a random string of 40 characters)
            github_token = "".join(
                random.choices(string.ascii_letters + string.digits, k=40)
            )
        else:
            # Retrieve token from environment variables
            github_token = os.getenv("GITHUB_TOKEN")

        if not github_token:
            raise ValueError("GITHUB_TOKEN is missing! Please set it in the .env file.")

        headers = {"Authorization": f"token {github_token}"}

    # Set the query parameters based on function inputs
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

    # Filter out any None values from the params dictionary
    params = {key: value for key, value in params.items() if value is not None}

    # Handle the direction parameter
    if direction:
        params["direction"] = direction
    elif sort == "full_name":
        params["direction"] = "asc"  # Default direction for 'full_name'
    else:
        params["direction"] = "desc"  # Default direction for other sorts

    # Prepare the URL to send the GET request
    url = f"{BASE_URL}/user/repos"

    # Make the GET request to the GitHub API
    response = requests.get(url, params=params, headers=headers)

    # Attach the response details to Allure for visibility
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
    Fetches the list of commits for a given repository.

    Parameters:
    - owner (str): Repository owner username (case-insensitive).
    - repo (str): Repository name without `.git` extension (case-insensitive).
    - sha (str, optional): SHA or branch to start listing commits from. Default: repository's default branch.
    - path (str, optional): Filter commits that modify a specific file/directory.
    - author (str, optional): GitHub username or email address to filter by commit author.
    - committer (str, optional): GitHub username or email address to filter by commit committer.
    - since (str, optional): Show commits after this timestamp (ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ).
    - until (str, optional): Show commits before this timestamp (ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ).
    - per_page (int, optional): Number of commits per page (max 100). Default is 30.
    - page (int, optional): Page number for pagination. Default is 1.
    - include_token (bool, optional): Whether to include the authentication token in the request.
    - random_token ( bool, optional):  # Whether to generate a random token for testing

    Returns:
    - Response object from the API request.
    """

    # Prepare headers
    headers = {}

    if include_token:
        if random_token:
            # Generate a random token for testing purposes (e.g., a random string of 40 characters)
            github_token = "".join(
                random.choices(string.ascii_letters + string.digits, k=40)
            )
        else:
            # Retrieve token from environment variables
            github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise ValueError("GITHUB_TOKEN is missing! Please set it in the .env file.")
        headers["Authorization"] = f"Bearer {github_token}"

    # Set query parameters, filtering out None values
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
    params = {
        key: value for key, value in params.items() if value is not None
    }  # Remove None values

    # Construct the API endpoint
    url = f"{BASE_URL}/repos/{owner}/{repo}/commits"

    with allure.step(f"Sending GET request to fetch commits for {owner}/{repo}"):
        response = requests.get(url, params=params, headers=headers)

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
