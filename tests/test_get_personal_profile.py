import string

import allure
import pytest

from error_messages.messages import ErrorMessages
from models.user_model import UserProfile, AuthorizedUserProfile
from schemas.user_schema import USER_PROFILE_SCHEMA, NEGATIVE_RESPONSE_SCHEMA
from utils.api_users import get_logged_user_profile, update_user_profile
from utils.schema_validator import validate_json_schema


@pytest.mark.smoke
def test_get_own_personal_profile_contains_expected_fields():
    with allure.step(
        f"Send GET request to fetch the personal profile based on the github token provided in the authorization headers"
    ):
        response = get_logged_user_profile()

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step(
        "Validate JSON schema of the response, that contains one more field called notification email"
    ):
        data = response.json()
        validate_json_schema(data, USER_PROFILE_SCHEMA)

    with allure.step("Convert JSON response to UserProfile object and verify data"):
        # Create an instance of UserProfile using the response data
        user_profile = AuthorizedUserProfile(**data)
        allure.attach(
            str(user_profile),
            name="UserProfile Object",
            attachment_type=allure.attachment_type.TEXT,
        )

        # Verify that the 'login' field matches the provided username (ignoring case)
        assert (
            user_profile.login.lower() == "aleixbernardo"
        ), f"Expected login to be aleixbernardo, but got {user_profile.login}"
    with allure.step("Check the private data is not null"):
        assert user_profile.private_gists is not None
        assert user_profile.owned_private_repos is not None
        assert user_profile.total_private_repos is not None
        assert user_profile.disk_usage is not None
        assert user_profile.collaborators is not None
        assert user_profile.two_factor_authentication is False
        assert user_profile.plan["name"] == "free"


@pytest.mark.smoke
def test_update_own_personal_profile_name(reset_github_attributes):
    with allure.step(
        f"Send GET request to fetch the personal profile based on the github token provided in the authorization headers"
    ):
        response = get_logged_user_profile()

    with allure.step("Check the status code is as expected"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Check the initial name is aleix"):
        user_profile = AuthorizedUserProfile(**response.json())
        allure.attach(
            str(user_profile),
            name="UserProfile Object",
            attachment_type=allure.attachment_type.TEXT,
        )

        # Verify that the 'login' field matches the provided username (ignoring case)
        assert (
            user_profile.name == "aleix"
        ), f"Expected name to be aleix, but got {user_profile.name}"

    with allure.step(f"Send PATCH request to update the name"):
        response = update_user_profile({"name": "name updated"})

    with allure.step("Check the status code is as expected"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step(
        f"Send GET request to fetch the new personal profile based on the github token provided in the authorization headers"
    ):
        response = get_logged_user_profile()

    with allure.step("Check the status code is as expected"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Check the updated name"):
        user_profile = AuthorizedUserProfile(**response.json())
        allure.attach(
            str(user_profile),
            name="UserProfile Object",
            attachment_type=allure.attachment_type.TEXT,
        )

        # Verify that the 'login' field matches the provided username (ignoring case)
        assert (
            user_profile.name == "name updated"
        ), f"Expected name to be name updated, but got {user_profile.name}"


@pytest.mark.security
def test_get_own_personal_no_token_attached():
    with allure.step(f"Send GET request to fetch the personal profile without token"):
        response = get_logged_user_profile(include_token=False)

    with allure.step("Validate the HTTP status code is 401 unauthorized"):
        assert response.status_code == 401, f"Expected 200, got {response.status_code}"

    with allure.step(
        "Validate JSON schema of the response, that contains one more field called notification email"
    ):
        data = response.json()
        validate_json_schema(data, NEGATIVE_RESPONSE_SCHEMA)

    with allure.step("Check error message is the expected"):
        assert data["message"] == ErrorMessages.MISSING_TOKEN_ERROR


@pytest.mark.security
def test_get_own_personal_incorrect_token():
    with allure.step(f"Send GET request to fetch the personal profile without token"):
        response = get_logged_user_profile(random_token=True)

    with allure.step("Validate the HTTP status code is 401 unauthorized"):
        assert response.status_code == 401, f"Expected 200, got {response.status_code}"

    with allure.step(
        "Validate JSON schema of the response, that contains one more field called notification email"
    ):
        data = response.json()
        validate_json_schema(data, NEGATIVE_RESPONSE_SCHEMA)

    with allure.step("Check error message is the expected"):
        assert data["message"] == ErrorMessages.INVALID_CREDENTIALS


@pytest.mark.security
def test_update_name_no_token_attached(reset_github_attributes):
    with allure.step(
        f"Send PATCH request to update the personal profile without token"
    ):
        response = update_user_profile({"name": "name updated"}, include_token=False)

    with allure.step("Validate the HTTP status code is 401 unauthorized"):
        assert response.status_code == 401, f"Expected 200, got {response.status_code}"

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
def test_update_name_incorrect_token(reset_github_attributes):
    with allure.step(
        f"Send PATCH request to update the personal profile without token"
    ):
        response = update_user_profile({"name": "name updated"}, random_token=True)

    with allure.step("Validate the HTTP status code is 401 unauthorized"):
        assert response.status_code == 401, f"Expected 200, got {response.status_code}"

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
        response = get_logged_user_profile()
    with allure.step("Check that the total elapsed time is less than 1 second"):
        assert response.status_code == 200, f"Expected 404, got {response.status_code}"
        assert (
            response.elapsed.total_seconds() < 1
        ), "API response time exceeded 1 seconds"
