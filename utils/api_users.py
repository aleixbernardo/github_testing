import os
import random
import string

import allure
import requests

BASE_URL = "https://api.github.com/"


def get_user_profile(username: str, include_token=True):
    """Get the public profile of a username using the github personal access token saved in .env file"""
    headers = {}
    if include_token:
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise ValueError("GITHUB_TOKEN is missing! Please set it in the .env file.")
        headers = {"Authorization": f"token {github_token}"}
    url = f"{BASE_URL}/users/{username}"
    response = requests.get(url, headers=headers)
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
    Get the personal profile based on the GitHub token provided in the authorization headers.

    :param include_token: Whether or not to include a valid token in the request headers. Default is True.
    :param random_token: If True, generate a random token for testing. Default is False.
    :return: Response object from the GET request.
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
    url = f"{BASE_URL}/user"
    response = requests.get(url, headers=headers)
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
    Update the personal profile based on the GitHub token provided in the authorization headers.

    :param body: body parameters of the request, can contain name, email, blog...
    :param include_token: Whether or not to include a valid token in the request headers. Default is True.
    :param random_token: If True, generate a random token for testing. Default is False.
    :return: Response object from the GET request.
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
    url = f"{BASE_URL}/user"
    response = requests.patch(url, headers=headers, json=body)
    allure.attach(
        str(response.status_code),
        name="Status Code",
        attachment_type=allure.attachment_type.TEXT,
    )
    allure.attach(
        response.text, name="Response Body", attachment_type=allure.attachment_type.JSON
    )

    return response
