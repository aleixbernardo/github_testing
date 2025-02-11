import allure
import pytest

from error_messages.messages import ErrorMessages
from models.user_model import UserProfile, AuthorizedUserProfile
from schemas.user_schema import USER_PROFILE_SCHEMA, NEGATIVE_RESPONSE_SCHEMA
from utils.api_users import get_logged_user_profile, update_user_profile
from utils.schema_validator import validate_json_schema


# Define the epic and story to categorize the tests for Allure reporting
@allure.epic("GitHub API")
@allure.feature("Personal Profile")
class TestPersonalProfile:

    @pytest.mark.smoke
    @allure.story("Fetching personal profile with a valid token")
    def test_get_own_personal_profile_contains_expected_fields(self):
        with allure.step(
            f"Send GET request to fetch the personal profile based on the github token provided in the authorization headers"
        ):
            response = get_logged_user_profile()

        with allure.step("Validate the HTTP status code is 200"):
            assert (
                response.status_code == 200
            ), f"Expected 200, got {response.status_code}"

        with allure.step(
            "Validate JSON schema of the response"
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

    @pytest.mark.security
    @allure.story("Fetching personal profile without token")
    def test_get_own_personal_no_token_attached(self):
        with allure.step(
            f"Send GET request to fetch the personal profile without token"
        ):
            response = get_logged_user_profile(include_token=False)

        with allure.step("Validate the HTTP status code is 401 unauthorized"):
            assert (
                response.status_code == 401
            ), f"Expected 401, got {response.status_code}"

        with allure.step(
            "Validate JSON schema of the response for the negative response"
        ):
            data = response.json()
            validate_json_schema(data, NEGATIVE_RESPONSE_SCHEMA)

        with allure.step("Check error message is the expected"):
            assert data["message"] == ErrorMessages.MISSING_TOKEN_ERROR

    @pytest.mark.security
    @allure.story("Fetching personal profile with incorrect token")
    def test_get_own_personal_incorrect_token(self):
        with allure.step(
            f"Send GET request to fetch the personal profile with incorrect token"
        ):
            response = get_logged_user_profile(random_token=True)

        with allure.step("Validate the HTTP status code is 401 unauthorized"):
            assert (
                response.status_code == 401
            ), f"Expected 200, got {response.status_code}"

        with allure.step(
            "Validate JSON schema of the response for the negative response"
        ):
            data = response.json()
            validate_json_schema(data, NEGATIVE_RESPONSE_SCHEMA)

        with allure.step("Check error message is the expected"):
            assert data["message"] == ErrorMessages.INVALID_CREDENTIALS

    @pytest.mark.performance
    @allure.story("Check response time for fetching personal profile")
    def test_response_time(self):
        with allure.step(f"Send GET request to fetch personal user profile"):
            response = get_logged_user_profile()

        with allure.step("Check that the total elapsed time is less than 1 second"):
            assert (
                response.status_code == 200
            ), f"Expected 404, got {response.status_code}"
            assert (
                response.elapsed.total_seconds() < 1
            ), "API response time exceeded 1 second"
