import string
from pprint import pprint

import allure
import pytest

from error_messages.messages import ErrorMessages
from models.repo_model import Repository
from models.user_model import AuthorizedUserProfile, UserProfile
from schemas.repos_schema import LIST_REPOSITORIES_SCHEMA
from schemas.user_schema import USER_PROFILE_SCHEMA, NEGATIVE_RESPONSE_SCHEMA
from utils.api_repos import get_repositories_from_user
from utils.schema_validator import validate_json_schema, from_dict


@allure.epic("GitHub API Testing")
@allure.feature("Repositories API")
class TestGitHubRepositories:

    @allure.story("Retrieve public repositories of a user")
    @pytest.mark.parametrize("username", ["octocat", "aleixbernardo"])
    @pytest.mark.smoke
    def test_get_public_repositories_of_user_contains_expected_fields(self, username):
        with allure.step(f"Send GET request to fetch repositories for '{username}'"):
            response = get_repositories_from_user(username)

        with allure.step("Validate the HTTP status code is 200"):
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        with allure.step("Validate JSON schema of the response"):
            data = response.json()
            validate_json_schema(data, LIST_REPOSITORIES_SCHEMA)

    @allure.story("Retrieve repositories with and without authorization")
    @pytest.mark.parametrize("username", ["octocat", "aleixbernardo"])
    @pytest.mark.security
    def test_get_public_repositories_of_user_with_and_without_authorization(self, username):
        with allure.step(f"Send GET request for '{username}' with authorization"):
            response = get_repositories_from_user(username)
            assert response.status_code == 200

        with allure.step(f"Send GET request for '{username}' without authorization"):
            response_no_auth = get_repositories_from_user(username, include_token=False)
            assert response_no_auth.status_code == 200

    @allure.story("Handle invalid credentials")
    @pytest.mark.security
    def test_get_public_repositories_of_user_invalid_credentials(self):
        with allure.step("Send GET request with invalid credentials"):
            response = get_repositories_from_user("aleixbernardo", random_token=True)

        with allure.step("Validate unauthorized status code"):
            assert response.status_code == 401, f"Expected 401, got {response.status_code}"

        with allure.step("Check error message"):
            data = response.json()
            assert data["message"] == ErrorMessages.INVALID_CREDENTIALS

    @allure.story("Retrieve user repositories with limited count")
    def test_get_public_repositories_of_user_only_1_repo(self):
        with allure.step("Send GET request for 'aleixbernardo'"):
            response = get_repositories_from_user("aleixbernardo")

        with allure.step("Validate the HTTP status code is 200"):
            assert response.status_code == 200

        with allure.step("Validate JSON schema"):
            data = response.json()
            validate_json_schema(data, LIST_REPOSITORIES_SCHEMA)

        with allure.step("Check repository count is correct"):
            assert len(data) == 1

        with allure.step("Convert JSON response to Repository object and verify"):
            repo_object = from_dict(data[0], Repository)
            allure.attach(str(repo_object), name="Repository Object", attachment_type=allure.attachment_type.TEXT)

            assert repo_object.full_name == "aleixbernardo/github_testing"
            assert repo_object.owner.login == "aleixbernardo"

    test_cases = [
        (1, 3, 3),
        (2, 3, 3),
        (3, 3, 2),
        (4, 3, 0),
        (1, 8, 8),
    ]

    @allure.story("Paginate public repositories")
    @pytest.mark.parametrize("page, per_page, expected_count", test_cases)
    def test_get_public_repositories_of_user_pagination(self, page, per_page, expected_count):
        with allure.step(f"Send GET request for page {page}"):
            response = get_repositories_from_user("octocat", page=page, per_page=per_page)

        with allure.step("Validate HTTP status and JSON schema"):
            assert response.status_code == 200
            data = response.json()
            validate_json_schema(data, LIST_REPOSITORIES_SCHEMA)

        with allure.step(f"Check repository count for page {page}"):
            assert len(data) == expected_count, f"Expected {expected_count}, got {len(data)}"

    test_sorting_cases = [
        ("created", "asc"),
        ("created", "desc"),
        ("updated", "asc"),
        ("updated", "desc"),
        ("pushed", "asc"),
        ("pushed", "desc"),
        ("full_name", "asc"),
        ("full_name", "desc"),
    ]

    @allure.story("Sort repositories")
    @pytest.mark.parametrize("sort, direction", test_sorting_cases)
    def test_get_public_repositories_of_user_sorting(self, sort, direction):
        with allure.step(f"Fetch repositories sorted by {sort} in {direction} order"):
            response = get_repositories_from_user("octocat", sort=sort, direction=direction)
            assert response.status_code == 200

        with allure.step("Convert to repository objects and validate sorting"):
            data = response.json()
            repo_objects = [from_dict(repo, Repository) for repo in data]

            field_ordering = sort + "_at" if sort != "full_name" else sort
            sorted_repo_objects = sorted(
                repo_objects,
                key=lambda x: (
                    getattr(x, field_ordering).lower()
                    if isinstance(getattr(x, field_ordering), str)
                    else getattr(x, field_ordering)
                ),
                reverse=(direction == "desc"),
            )

            assert repo_objects == sorted_repo_objects, f"Sorting failed for {sort} {direction}"

    test_filter_cases = [
        ("all", "All repositories"),
        ("owner", "Owned repositories"),
        ("member", "Repositories from organizations"),
    ]

    @allure.story("Filter repositories by type")
    @pytest.mark.parametrize("type_value, description", test_filter_cases)
    def test_get_repositories_with_type_filter(self, type_value, description):
        with allure.step(f"Fetch repositories with type filter '{type_value}'"):
            response = get_repositories_from_user("octocat", type=type_value, per_page=50)
            assert response.status_code == 200

        with allure.step(f"Validate repositories match filter '{type_value}'"):
            data = response.json()
            repo_objects = [from_dict(repo, Repository) for repo in data]

            if type_value == "owner":
                assert all(repo.owner.login == "octocat" for repo in repo_objects)
            elif type_value == "member":
                assert not any(repo.owner.login == "octocat" for repo in repo_objects)

            assert repo_objects, f"No repositories found for filter '{type_value}'"
