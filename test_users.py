import allure
import pytest

from models.user_model import UserProfile
from schemas.user_schema import USER_PROFILE_SCHEMA, NEGATIVE_RESPONSE_SCHEMA
from utils.api_client import get_user_profile
from utils.schema_validator import validate_json_schema

@pytest.mark.parametrize("username", ["octocat", "aleixbernardo"])
@pytest.mark.smoke
def test_get_user_profile_existing_users(username):
    with allure.step(f"Send GET request to fetch user profile for '{username}'"):
        response = get_user_profile(username)
        allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        allure.attach(str(response.status_code), name="Status Code", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Validate 'Content-Type' header contains 'application/json'"):
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type, f"Expected 'application/json' in Content-Type, got {content_type}"
        allure.attach(content_type, name="Content-Type Header", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        validate_json_schema(data, USER_PROFILE_SCHEMA)
        allure.attach(response.text, name="Validated JSON Schema", attachment_type=allure.attachment_type.JSON)

    with allure.step("Convert JSON response to UserProfile object and verify data"):
        # Create an instance of UserProfile using the response data
        user_profile = UserProfile(**data)
        allure.attach(str(user_profile), name="UserProfile Object", attachment_type=allure.attachment_type.TEXT)

        # Verify that the 'login' field matches the provided username (ignoring case)
        assert user_profile.login.lower() == username.lower(), (
            f"Expected login to be {username.lower()}, but got {user_profile.login}"
        )

@pytest.mark.parametrize("username", ["", "aleixbernardo123"])
def test_get_user_profile_non_existing_users(username):
    with allure.step(f"Send GET request to fetch user profile for '{username}'"):
        response = get_user_profile(username)
        allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)

    with allure.step("Validate the HTTP status code is 404"):
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        allure.attach(str(response.status_code), name="Status Code", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        validate_json_schema(data, NEGATIVE_RESPONSE_SCHEMA)