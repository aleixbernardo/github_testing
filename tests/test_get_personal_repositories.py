import string
from datetime import datetime
from pprint import pprint

import allure
import pytest

from error_messages.messages import ErrorMessages
from models.repo_model import Repository
from models.user_model import AuthorizedUserProfile, UserProfile
from schemas.repos_schema import LIST_REPOSITORIES_SCHEMA
from schemas.user_schema import USER_PROFILE_SCHEMA, NEGATIVE_RESPONSE_SCHEMA
from utils.api_repos import get_repositories_from_logged_user
from utils.schema_validator import validate_json_schema


@pytest.mark.smoke
def test_get_personal_repositories():
    with allure.step(f"Send GET request to fetch user profile for logged in user'"):
        response = get_repositories_from_logged_user()

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        validate_json_schema(data, LIST_REPOSITORIES_SCHEMA)

        assert len(data) == 9


@pytest.mark.security
def test_get_personal_repositories_of_logged_user_with_and_without_authorization():
    with allure.step(f"Send GET request to get the personal repositories without including token"):
        response = get_repositories_from_logged_user(include_token=False)

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        validate_json_schema(data, NEGATIVE_RESPONSE_SCHEMA)

    with allure.step(f"Send GET request to get the personal repositories with random token"):
        response = get_repositories_from_logged_user(include_token=True, random_token=True)

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        validate_json_schema(data, NEGATIVE_RESPONSE_SCHEMA)


test_cases = [
    (1, 3, 3),  # Page 1, 3 per page, expect 3 repos
    (2, 3, 3),  # Page 2, 3 per page, expect 3 repos
    (3, 3, 3),  # Page 3, 3 per page, expect 2 repos
    (4, 3, 0),  # Page 4, 3 per page, expect 0 repos
    (1, 9, 9),  # Page 1, 8 per page, expect 8 repos
]


@pytest.mark.parametrize("page, per_page, expected_count", test_cases)
def test_get_personal_repositories_of_logged_user_of_user_pagination(page, per_page, expected_count):
    """
    aleix bernardo contains 9 repos
    """
    with allure.step(f"Send GET request to fetch user repositories - Page {page}"):
        response = get_repositories_from_logged_user(page=page, per_page=per_page)

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        validate_json_schema(data, LIST_REPOSITORIES_SCHEMA)

    with allure.step(f"Check the number of repos in page {page} is {expected_count}"):
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


@pytest.mark.parametrize("sort, direction", test_sorting_cases)
def test_get_personal_repositories_of_logged_user_of_user_sorting(sort, direction):
    """
     aleix bernardo contains 9 repos
    """
    with allure.step(f"Send GET request to fetch sorted repositories - Sort: {sort}, Direction: {direction}"):
        response = get_repositories_from_logged_user(sort=sort, direction=direction)

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        validate_json_schema(data, LIST_REPOSITORIES_SCHEMA)

    with allure.step(f"Convert JSON response to list of Repo objects"):
        repo_objects = [Repository(**repo) for repo in data]

    with allure.step(f"Check that repositories are sorted by {sort} in {direction} order"):
        # Adjust field name if sorting by 'full_name'
        field_ordering = sort + "_at" if sort != 'full_name' else sort

        # Sort the repositories, applying `lower()` to string fields for case-insensitive sorting
        sorted_repo_objects = sorted(
            repo_objects,
            key=lambda x: getattr(x, field_ordering).lower() if isinstance(getattr(x, field_ordering),
                                                                           str) else getattr(x, field_ordering),
            reverse=(direction == "desc")
        )

        # Assert that the response data matches the sorted data
        assert repo_objects == sorted_repo_objects, f"Repositories are not sorted correctly by {sort} in {direction} order"


test_filter_cases = [
    ("all", "All repositories"),
    ("owner", "Repositories owned by the user"),  # Default filter
    ("public", "Public repositories"),
    ("private", "Private repos"),
    ("member", "Repositories owned by organizations the user is a member of")
]


@pytest.mark.parametrize("type_value, description", test_filter_cases)
def test_get_personal_repositories_with_type_filter(type_value, description):
    """
    Test filtering repositories by 'type' query parameter.
    from the 9 projects, 4 is member of mberanrdo95
    """
    with allure.step(f"Send GET request to fetch repositories of type: {type_value}"):
        response = get_repositories_from_logged_user(type=type_value, per_page=50)

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        validate_json_schema(data, LIST_REPOSITORIES_SCHEMA)

    with allure.step(f"Convert JSON response to list of Repo objects"):
        repo_objects = [Repository(**repo) for repo in data]

    with allure.step(f"Validate that repositories are filtered by type '{type_value}' ({description})"):
        # Implement logic here to check if the repositories match the 'type' filter
        if type_value == "all":
            # If the 'type' is 'all', repositories can be owned by anyone
            pass  # No specific check needed for 'all' type
            assert len(repo_objects) == 9
        elif type_value == "owner":
            assert all(repo.owner["login"] == "aleixbernardo" for repo in repo_objects), \
                f"Not all repositories are owned by 'octocat' for filter '{type_value}'"
            assert len(repo_objects) == 5
        elif type_value == "member":
            # For the 'member' type, check if the repository is not owned by him
            assert all(repo.owner["login"] == "mbernardo95" for repo in repo_objects)
            assert len(repo_objects) == 4

        elif type_value == "public":
            # For the 'member' type, check if the repository is not owned by him
            assert all(repo.owner["login"] == "aleixbernardo" for repo in repo_objects)
            assert len(repo_objects) == 1
            assert repo_objects[0].full_name == "aleixbernardo/github_testing"


        elif type_value == "private":
            # For the 'member' type, check if the repository is not owned by him
            assert len(repo_objects) == 8


test_filter_cases = [
    ("all", "All repositories"),
    ("public", "Public repositories"),
    ("private", "Private repos"), ]


@pytest.mark.parametrize("visibility_value, description", test_filter_cases)
def test_get_personal_repositories_with_visibility_filter(visibility_value, description):
    """
    Test filtering repositories by 'type' query parameter.
    from the 9 projects, 4 is member of mberanrdo95
    """
    with allure.step(f"Send GET request to fetch repositories of visibility: {visibility_value}"):
        response = get_repositories_from_logged_user(visibility=visibility_value, type=None, per_page=50)

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        validate_json_schema(data, LIST_REPOSITORIES_SCHEMA)

    with allure.step(f"Convert JSON response to list of Repo objects"):
        repo_objects = [Repository(**repo) for repo in data]

    with allure.step(f"Validate that repositories are filtered by type '{visibility_value}' ({description})"):
        # Implement logic here to check if the repositories match the 'type' filter
        if visibility_value == "public":
            # For the 'member' type, check if the repository is not owned by him
            assert all(repo.owner["login"] == "aleixbernardo" for repo in repo_objects)
            assert len(repo_objects) == 1
            assert repo_objects[0].full_name == "aleixbernardo/github_testing"


        elif visibility_value == "private":
            # For the 'member' type, check if the repository is not owned by him
            assert len(repo_objects) == 8
        else:
            assert len(repo_objects) == 9


test_filter_cases = [
    ("owner", "owner repositories"),
    ("collaborator", "collaborator repositories"),
    ("organization_member", "organization_member repos"), ]


@pytest.mark.parametrize("affiliation_value, description", test_filter_cases)
def test_get_personal_repositories_with_affiliation_filter(affiliation_value, description):
    """
    Test filtering repositories by 'type' query parameter.
    from the 9 projects, 4 is member of mberanrdo95
    """
    with allure.step(f"Send GET request to fetch repositories of affiliation_value: {affiliation_value}"):
        response = get_repositories_from_logged_user(affiliation=affiliation_value, type=None, per_page=50)

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        validate_json_schema(data, LIST_REPOSITORIES_SCHEMA)

    with allure.step(f"Convert JSON response to list of Repo objects"):
        repo_objects = [Repository(**repo) for repo in data]

    with allure.step(
            f"Validate that repositories are filtered by affiliation_value '{affiliation_value}' ({description})"):
        # Implement logic here to check if the repositories match the 'type' filter
        if affiliation_value == "owner":
            # For the 'member' type, check if the repository is not owned by him
            assert all(repo.owner["login"] == "aleixbernardo" for repo in repo_objects)
            assert len(repo_objects) == 5

        elif affiliation_value == "collaborator":
            # For the 'member' type, check if the repository is not owned by him
            assert all(repo.owner["login"] == "mbernardo95" for repo in repo_objects)
            assert len(repo_objects) == 4
        else:
            assert len(repo_objects) == 0


def test_combination_type_and_affiliation():
    with allure.step(f"Send GET request to fetch repositories of affiliation owner and type public"):
        response = get_repositories_from_logged_user(affiliation="owner", type='public', per_page=50)

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    with allure.step("Check error message"):
        with allure.step("Check error message is the expected"):
            assert response.json()["message"] == ErrorMessages.INVALID_VISIBILITY_AFFILIATION_TYPE_COMBINATION


def test_combination_type_and_visibility():
    with allure.step(f"Send GET request to fetch repositories of affiliation owner and type public"):
        response = get_repositories_from_logged_user(visibility="private", type='public', per_page=50)

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    with allure.step("Check error message"):
        with allure.step("Check error message is the expected"):
            assert response.json()["message"] == ErrorMessages.INVALID_VISIBILITY_AFFILIATION_TYPE_COMBINATION



test_filter_cases = [
    ("2022-05-01T17:52:41Z", 9),  # All repositories since this timestamp
    ("2025-01-01T18:29:27Z", 4),  # Only repositories updated after this time
]

@pytest.mark.parametrize("since_value, number_repos", test_filter_cases)
def test_get_personal_repositories_since_filter(since_value, number_repos):
    """
    The updated dates for the repos are:
       2022-05-01T20:20:58Z
       2022-09-20T14:20:15Z
       2022-09-20T14:41:52Z
       2025-01-01T15:39:16Z
       2025-01-01T17:29:27Z
       2025-01-25T12:35:02Z
       2025-01-25T14:45:36Z
       2025-01-25T14:47:52Z
       2025-02-10T14:27:22Z
    """
    with allure.step(f"Send GET request to fetch repositories"):
        response = get_repositories_from_logged_user(since=since_value, per_page=50)
        data = response.json()

    with allure.step(f"Convert JSON response to list of Repo objects"):
        repo_objects = [Repository(**repo) for repo in data]
        assert len(repo_objects) == number_repos

    with allure.step("Check all dates are after the since value"):
        since_value_dt = datetime.strptime(since_value, "%Y-%m-%dT%H:%M:%SZ")
        for repo in repo_objects:
            repo_updated_dt = datetime.strptime(repo.updated_at, "%Y-%m-%dT%H:%M:%SZ")
            assert repo_updated_dt > since_value_dt, f"Repo updated_at {repo.updated_at} is not after {since_value}"


test_filter_cases = [
    ("2026-02-10T14:27:22Z", 9),  # all repositories updated before this timestamp
    ("2022-09-20T15:41:52Z", 3),
]
@pytest.mark.parametrize("before_value, number_repos", test_filter_cases)
def test_get_personal_repositories_before_filter(before_value, number_repos):
    """
    The updated dates for the repos are:
       2022-05-01T20:20:58Z
       2022-09-20T14:20:15Z
       2022-09-20T14:41:52Z
       2025-01-01T15:39:16Z
       2025-01-01T17:29:27Z
       2025-01-25T12:35:02Z
       2025-01-25T14:45:36Z
       2025-01-25T14:47:52Z
       2025-02-10T14:27:22Z
    """
    with allure.step(f"Send GET request to fetch repositories"):
        response = get_repositories_from_logged_user(before=before_value, per_page=50)
        data = response.json()

    with allure.step(f"Convert JSON response to list of Repo objects"):
        repo_objects = [Repository(**repo) for repo in data]
        assert len(repo_objects) == number_repos

    with allure.step("Check all dates are after the since value"):
        before_value_dt = datetime.strptime(before_value, "%Y-%m-%dT%H:%M:%SZ")
        for repo in repo_objects:
            repo_updated_dt = datetime.strptime(repo.updated_at, "%Y-%m-%dT%H:%M:%SZ")
            assert repo_updated_dt < before_value_dt, f"Repo updated_at {repo.updated_at} is not before {before_value}"