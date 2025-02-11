import os
import random
import string
import allure
import requests

BASE_URL = "https://api.github.com"


def get_user_profile(username: str, include_token=True):
    """
    Retrieves the public profile of a GitHub user based on their username.

    Parameters:
    - username (str): The GitHub username to fetch the profile of.
    - include_token (bool): Whether to include a GitHub token for authentication. Default is True.

    Returns:
    - Response object from the GET request, containing the user's profile information.
    """
    headers = {}

    # If include_token is True, fetch the GitHub token from environment variables and add it to the request headers
    if include_token:
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise ValueError("GITHUB_TOKEN is missing! Please set it in the .env file.")
        headers = {"Authorization": f"token {github_token}"}

    # Make the API request to get the user's profile
    url = f"{BASE_URL}/users/{username}"
    response = requests.get(url, headers=headers)

    # Attach response details to Allure for visibility
    allure.attach(
        str(response.status_code),
        name="Status Code",
        attachment_type=allure.attachment_type.TEXT,
    )
    allure.attach(
        response.text, name="Response Body", attachment_type=allure.attachment_type.JSON
    )

    return response


def get_logged_user_profile(include_token=True, random_token=False):
    """
    Retrieves the profile of the currently authenticated GitHub user based on the GitHub token provided.

    Parameters:
    - include_token (bool): Whether to include a valid token in the request headers. Default is True.
    - random_token (bool): If True, generate a random token for testing purposes. Default is False.

    Returns:
    - Response object from the GET request containing the logged-in user's profile information.
    """
    headers = {}

    if include_token:
        # Generate a random token or retrieve the token from environment variables based on random_token flag
        if random_token:
            github_token = "".join(
                random.choices(string.ascii_letters + string.digits, k=40)
            )
        else:
            github_token = os.getenv("GITHUB_TOKEN")

        if not github_token:
            raise ValueError("GITHUB_TOKEN is missing! Please set it in the .env file.")

        headers = {"Authorization": f"token {github_token}"}

    # Make the API request to get the logged-in user's profile
    url = f"{BASE_URL}/user"
    response = requests.get(url, headers=headers)

    # Attach response details to Allure for visibility
    allure.attach(
        str(response.status_code),
        name="Status Code",
        attachment_type=allure.attachment_type.TEXT,
    )
    allure.attach(
        response.text, name="Response Body", attachment_type=allure.attachment_type.JSON
    )

    return response


def update_user_profile(body, include_token=True, random_token=False):
    """
    Updates the profile of the currently authenticated GitHub user with the provided data.

    Parameters:
    - body (dict): A dictionary containing the fields to be updated (e.g., name, email, blog).
    - include_token (bool): Whether to include a valid token in the request headers. Default is True.
    - random_token (bool): If True, generate a random token for testing purposes. Default is False.

    Returns:
    - Response object from the PATCH request containing the result of the update.
    """
    headers = {}

    if include_token:
        # Generate a random token or retrieve the token from environment variables based on random_token flag
        if random_token:
            github_token = "".join(
                random.choices(string.ascii_letters + string.digits, k=40)
            )
        else:
            github_token = os.getenv("GITHUB_TOKEN")

        if not github_token:
            raise ValueError("GITHUB_TOKEN is missing! Please set it in the .env file.")

        headers = {"Authorization": f"token {github_token}"}

    # Make the API request to update the user's profile
    url = f"{BASE_URL}/user"
    response = requests.patch(url, headers=headers, json=body)

    # Attach response details to Allure for visibility
    allure.attach(
        str(response.status_code),
        name="Status Code",
        attachment_type=allure.attachment_type.TEXT,
    )
    allure.attach(
        response.text, name="Response Body", attachment_type=allure.attachment_type.JSON
    )

    return response
