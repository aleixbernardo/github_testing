import os
import string

import allure
import pytest
import requests

from error_messages.messages import ErrorMessages
from models.user_model import UserProfile, AuthorizedUserProfile
from schemas.user_schema import USER_PROFILE_SCHEMA, NEGATIVE_RESPONSE_SCHEMA
from utils.api_users import get_logged_user_profile, update_user_profile
from utils.schema_validator import validate_json_schema

update_profile_cases = [
    ("name", "aleix", "name updated"),  # Update name
    ("blog", "aleix.bernardo@blog.com", "https://new-blog.com"),  # Update blog
    ("twitter_username", "aleix_twitter", "newtwitterhandle"),  # Update twitter handle
    ("company", "Bizerba", "New Company"),  # Update company
    ("location", "Badalona", "New Location"),  # Update location
    ("bio", "this is the bio of aleix", "A new bio"),  # Update bio
]


@pytest.mark.smoke
@pytest.mark.parametrize("attribute, old_value, new_value", update_profile_cases)
def test_update_own_personal_profile_attribute(
    attribute, old_value, new_value, reset_github_profile_attributes
):
    """
    Test that each att
    ribute of the user's personal profile can be updated, as fixture we reset the attributes so we know it has been changed
    """
    with allure.step(
        f"Send GET request to fetch the personal profile based on the GitHub token provided in the authorization headers"
    ):
        response = get_logged_user_profile()

    with allure.step("Check the status code is as expected"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Check the initial profile attributes"):
        user_profile = AuthorizedUserProfile(**response.json())
        allure.attach(
            str(user_profile),
            name="UserProfile Object",
            attachment_type=allure.attachment_type.TEXT,
        )

        # Verify that the initial attribute value is as expected (if applicable)
        assert (
            getattr(user_profile, attribute) == old_value
        ), f"Expected {attribute} to be present"

    with allure.step(f"Send PATCH request to update {attribute} to '{new_value}'"):
        response = update_user_profile({attribute: new_value})

    with allure.step("Check the status code is as expected"):
        # You can adjust this if some attributes are expected to fail validation (e.g., invalid values)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step(f"Send GET request to fetch the updated personal profile"):
        response = get_logged_user_profile()

    with allure.step("Check the status code is as expected"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step(f"Check the updated {attribute} is '{new_value}'"):
        user_profile = AuthorizedUserProfile(**response.json())
        allure.attach(
            str(user_profile),
            name="Updated UserProfile Object",
            attachment_type=allure.attachment_type.TEXT,
        )

        # Verify that the updated attribute matches the expected value
        assert (
            getattr(user_profile, attribute) == new_value
        ), f"Expected {attribute} to be {new_value}, but got {getattr(user_profile, attribute)}"


@pytest.mark.security
def test_update_name_no_token_attached():
    with allure.step(
        f"Send PATCH request to update the personal profile without token"
    ):
        response = update_user_profile({"name": "name updated"}, include_token=False)

    with allure.step("Validate the HTTP status code is 401 unauthorized"):
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    with allure.step(
        "Validate JSON schema of the response, that contains one more field called notification email"
    ):
        data = response.json()
        validate_json_schema(data, NEGATIVE_RESPONSE_SCHEMA)

    with allure.step("Check error message is the expected"):
        assert data["message"] == ErrorMessages.MISSING_TOKEN_ERROR

    with allure.step(
        f"Send GET request to fetch the new personal profile based on the github token provided in the authorization headers"
    ):
        response = get_logged_user_profile()

    with allure.step("Check the status code is as expected"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Check the name has not been updated"):
        user_profile = AuthorizedUserProfile(**response.json())
        allure.attach(
            str(user_profile),
            name="UserProfile Object",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert (
            user_profile.name == "aleix"
        ), f"Expected name to be name aleix, but got {user_profile.name}"


@pytest.mark.security
def test_update_name_incorrect_token():
    with allure.step(
        f"Send PATCH request to update the personal profile without token"
    ):
        response = update_user_profile({"name": "name updated"}, random_token=True)

    with allure.step("Validate the HTTP status code is 401 unauthorized"):
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    with allure.step(
        "Validate JSON schema of the response, that contains one more field called notification email"
    ):
        data = response.json()
        validate_json_schema(data, NEGATIVE_RESPONSE_SCHEMA)

    with allure.step("Check error message is the expected"):
        assert data["message"] == ErrorMessages.INVALID_CREDENTIALS

    with allure.step(
        f"Send GET request to fetch the new personal profile based on the github token provided in the authorization headers"
    ):
        response = get_logged_user_profile()

    with allure.step("Check the status code is as expected"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Check the name has not been updated"):
        user_profile = AuthorizedUserProfile(**response.json())
        allure.attach(
            str(user_profile),
            name="UserProfile Object",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert (
            user_profile.name == "aleix"
        ), f"Expected name to be name aleix, but got {user_profile.name}"


@pytest.mark.performance
def test_response_time():
    with allure.step(f"Send GET request to fetch personal user profile'"):
        response = update_user_profile({})
    with allure.step("Check that the total elapsed time is less than 1 second"):
        assert response.status_code == 200, f"Expected 404, got {response.status_code}"
        assert (
            response.elapsed.total_seconds() < 1
        ), "API response time exceeded 1 seconds"


def test_update_own_personal_profile_not_modified(reset_github_profile_attributes):
    """
    Test that each att
    ribute of the user's personal profile can be updated, as fixture we reset the attributes so we know it has been changed
    """

    # Set up the token and URL
    token = os.getenv("GITHUB_TOKEN")
    url = "https://api.github.com/user"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }

    with allure.step("Send initial GET request to retrieve profile"):
        # Retrieve the current profile to get the ETag
        response = requests.get(url, headers=headers)
        assert (
            response.status_code == 200
        ), f"Expected 200, but got {response.status_code}"

    with allure.step("Retrieve and store ETag from response headers"):
        etag = response.headers.get("ETag")
        assert etag is not None, "ETag header is missing in response"
        allure.attach(
            etag, name="Received ETag", attachment_type=allure.attachment_type.TEXT
        )

    with allure.step(
        "Send PATCH request with same data and If-None-Match header to check for 304"
    ):
        # Send a PATCH request with the same data as before and the If-None-Match header
        headers["If-None-Match"] = etag  # Use the stored ETag
        response = requests.patch(
            url,
            headers=headers,
            json={
                "name": "aleix",  # Ensure this matches exactly with what is in your profile
                "blog": "aleix.bernardo@blog.com",  # Same blog URL
                "twitter_username": "aleix_twitter",  # Same Twitter username
                "company": "Bizerba",  # Same company
                "location": "Badalona",  # Same location
                "bio": "this is the bio of aleix",  # Same bio
            },
        )

    with allure.step("Verify that response status is 304 Not Modified"):
        assert (
            response.status_code == 304
        ), f"Expected 304, but got {response.status_code}"
