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


@pytest.mark.parametrize("username", ["octocat", "aleixbernardo"])
@pytest.mark.smoke
def test_get_public_repositories_of_user_contains_expected_fields(username):
    with allure.step(f"Send GET request to fetch user profile for '{username}'"):
        response = get_repositories_from_user(username)

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        validate_json_schema(data, LIST_REPOSITORIES_SCHEMA)


@pytest.mark.parametrize("username", ["octocat", "aleixbernardo"])
@pytest.mark.security
def test_get_public_repositories_of_user_with_and_without_authorization(username):
    with allure.step(f"Send GET request to fetch user profile for '{username}'"):
        response = get_repositories_from_user(username)

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        print(data)
        validate_json_schema(data, LIST_REPOSITORIES_SCHEMA)

    with allure.step(
        f"Send GET request to fetch user profile for '{username}' without authorization"
    ):
        response = get_repositories_from_user(username, include_token=False)

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        validate_json_schema(data, LIST_REPOSITORIES_SCHEMA)


@pytest.mark.security
def test_get_public_repositories_of_user_invalid_credentials():
    with allure.step("Send GET request to fetch user profile for aleixbernardo"):
        response = get_repositories_from_user("aleixbernardo", random_token=True)

    with allure.step("Validate the HTTP status code is 401 unauthorized"):
        assert response.status_code == 401, f"Expected 200, got {response.status_code}"

    with allure.step(
        "Validate JSON schema of the response, that contains one more field called notification email"
    ):
        data = response.json()
        validate_json_schema(data, NEGATIVE_RESPONSE_SCHEMA)

    with allure.step("Check error message is the expected"):
        assert data["message"] == ErrorMessages.INVALID_CREDENTIALS


def test_get_public_repositories_of_user_only_1_repo():
    with allure.step(f"Send GET request to fetch user profile for 'aleixbernardo'"):
        response = get_repositories_from_user("aleixbernardo")

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        validate_json_schema(data, LIST_REPOSITORIES_SCHEMA)

    with allure.step("Check the number of repos in page 1 is correct"):
        assert len(data) == 1

    with allure.step("Convert JSON response to list of Repo object and verify data"):
        repo_object = from_dict(data[0], Repository)
        allure.attach(
            str(repo_object),
            name="UserProfile Object",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert repo_object.full_name == "aleixbernardo/github_testing"
        assert repo_object.owner.login == "aleixbernardo"


test_cases = [
    (1, 3, 3),  # Page 1, 3 per page, expect 3 repos
    (2, 3, 3),  # Page 2, 3 per page, expect 3 repos
    (3, 3, 2),  # Page 3, 3 per page, expect 2 repos
    (4, 3, 0),  # Page 4, 3 per page, expect 0 repos
    (1, 8, 8),  # Page 1, 8 per page, expect 8 repos
]


@pytest.mark.parametrize("page, per_page, expected_count", test_cases)
def test_get_public_repositories_of_user_octocat_pagination(
    page, per_page, expected_count
):
    """
    octocat contains 8 repos at the moment of the test creation.
    Using pagination of 3 repos per page, we need to go up to page 3 to see the last repo.
    """
    with allure.step(f"Send GET request to fetch user repositories - Page {page}"):
        response = get_repositories_from_user("octocat", page=page, per_page=per_page)

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        validate_json_schema(data, LIST_REPOSITORIES_SCHEMA)

    with allure.step(f"Check the number of repos in page {page} is {expected_count}"):
        assert (
            len(data) == expected_count
        ), f"Expected {expected_count}, got {len(data)}"


test_sorting_cases = [
    ("created", "asc"),
    ("created", "desc"),
    ("updated", "asc"),
    ("updated", "desc"),
    ("pushed", "asc"),
    ("pushed", "desc"),
    ("full_name", "asc"),  # Default behavior
    ("full_name", "desc"),
]


@pytest.mark.parametrize("sort, direction", test_sorting_cases)
def test_get_public_repositories_of_user_octocat_sorting(sort, direction):
    """
    Test sorting of octocat's repositories by different criteria using Repository model.
    """
    with allure.step(
        f"Send GET request to fetch sorted repositories - Sort: {sort}, Direction: {direction}"
    ):
        response = get_repositories_from_user("octocat", sort=sort, direction=direction)

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        validate_json_schema(data, LIST_REPOSITORIES_SCHEMA)

    with allure.step(f"Convert JSON response to list of Repo objects"):
        repo_objects = [from_dict(repo, Repository) for repo in data]

    with allure.step(
        f"Check that repositories are sorted by {sort} in {direction} order"
    ):
        # Adjust field name if sorting by 'full_name'
        field_ordering = sort + "_at" if sort != "full_name" else sort

        # Sort the repositories, applying `lower()` to string fields for case-insensitive sorting
        sorted_repo_objects = sorted(
            repo_objects,
            key=lambda x: (
                getattr(x, field_ordering).lower()
                if isinstance(getattr(x, field_ordering), str)
                else getattr(x, field_ordering)
            ),
            reverse=(direction == "desc"),
        )

        # Assert that the response data matches the sorted data
        assert (
            repo_objects == sorted_repo_objects
        ), f"Repositories are not sorted correctly by {sort} in {direction} order"


test_filter_cases = [
    ("all", "All repositories"),
    ("owner", "Repositories owned by the user"),  # Default filter
    ("member", "Repositories owned by organizations the user is a member of"),
]


@pytest.mark.parametrize("type_value, description", test_filter_cases)
def test_get_repositories_with_type_filter(type_value, description):
    """
    Test filtering repositories by 'type' query parameter.
    """
    with allure.step(f"Send GET request to fetch repositories of type: {type_value}"):
        response = get_repositories_from_user("octocat", type=type_value, per_page=50)

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        validate_json_schema(data, LIST_REPOSITORIES_SCHEMA)

    with allure.step(f"Convert JSON response to list of Repo objects"):
        repo_objects = [from_dict(repo, Repository) for repo in data]

    with allure.step(
        f"Validate that repositories are filtered by type '{type_value}' ({description})"
    ):
        # Implement logic here to check if the repositories match the 'type' filter
        if type_value == "owner":
            assert all(
                repo.owner.login == "octocat" for repo in repo_objects
            ), f"Not all repositories are owned by 'octocat' for filter '{type_value}'"
            assert len(repo_objects) == 8
        elif type_value == "member":
            # For the 'member' type, check if the repository is not owned by him
            assert not any(
                repo.owner.login == "octocat" for repo in repo_objects
            ), f"Not all repositories are owned by 'octocat' for filter '{type_value}'"
            assert len(repo_objects) == 50
        elif type_value == "all":
            # If the 'type' is 'all', repositories can be owned by anyone
            pass  # No specific check needed for 'all' type
            assert len(repo_objects) == 50

        # Check that there are repositories in the response
        assert repo_objects, f"No repositories found for type '{type_value}'"
