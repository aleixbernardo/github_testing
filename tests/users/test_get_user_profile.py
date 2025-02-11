import string
import allure
import pytest

from error_messages.messages import ErrorMessages
from models.user_model import AuthorizedUserProfile, UserProfile
from schemas.user_schema import USER_PROFILE_SCHEMA, NEGATIVE_RESPONSE_SCHEMA
from utils.api_users import get_user_profile
from utils.schema_validator import validate_json_schema


# Define the epic and story to categorize the tests for Allure reporting
@allure.epic("GitHub API")
@allure.feature("User Profile")
class TestUserProfile:
    @pytest.mark.parametrize("username", ["octocat", "aleixbernardo"])
    @pytest.mark.smoke
    @allure.story("Fetching existing user profiles without authorization")
    def test_get_user_profile_existing_users_non_authorized_user(self, username):
        with allure.step(f"Send GET request to fetch user profile for '{username}'"):
            response = get_user_profile(username, include_token=False)

        with allure.step("Validate the HTTP status code is 200"):
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        with allure.step("Validate JSON schema of the response"):
            data = response.json()
            validate_json_schema(data, USER_PROFILE_SCHEMA)

        with allure.step("Convert JSON response to UserProfile object and verify data"):
            # Create an instance of UserProfile using the response data
            user_profile = UserProfile(**data)
            allure.attach(
                str(user_profile),
                name="UserProfile Object",
                attachment_type=allure.attachment_type.TEXT,
            )

            # Verify that the 'login' field matches the provided username (ignoring case)
            assert (
                    user_profile.login.lower() == username.lower()
            ), f"Expected login to be {username.lower()}, but got {user_profile.login}"

    @pytest.mark.smoke
    @allure.story("Fetching own profile with valid authorization")
    def test_get_user_same_profile_as_token_requested(self):
        with allure.step(
                "Send GET request to fetch user profile for aleixbernardo with the authorization matching the aleixbernardo"
        ):
            response = get_user_profile("aleixbernardo")

        with allure.step("Validate the HTTP status code is 200"):
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        with allure.step("Validate JSON schema of the response"):
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
            assert user_profile.two_factor_authentication is not None
            assert user_profile.plan is not None

    @pytest.mark.parametrize(
        "username", ["", "aleixbernardo123", string.punctuation, "a" * 500]
    )
    @allure.story("Fetching non-existing user profiles")
    def test_get_user_profile_non_existing_users(self, username):
        with allure.step(f"Send GET request to fetch user profile for '{username}'"):
            response = get_user_profile(username)

        with allure.step("Validate the HTTP status code is 404"):
            assert response.status_code == 404, f"Expected 404, got {response.status_code}"

        with allure.step("Validate JSON schema of the response"):
            data = response.json()
            validate_json_schema(data, NEGATIVE_RESPONSE_SCHEMA)

        with allure.step("Check error message is the expected"):
            assert data["message"] == ErrorMessages.NOT_FOUND

    @pytest.mark.performance
    @allure.story("Check response time for fetching user profile")
    def test_response_time(self):
        with allure.step(f"Send GET request to fetch user profile for aleixbernardo'"):
            response = get_user_profile("aleixbernardo")

        with allure.step("Check that the total elapsed time is less than 1 second"):
            assert response.status_code == 200, f"Expected 404, got {response.status_code}"
            assert (
                    response.elapsed.total_seconds() < 1
            ), "API response time exceeded 1 second"
