import string
from datetime import datetime
from pprint import pprint

import allure
import pytest

from error_messages.messages import ErrorMessages
from models.commit_model import CommitDetail
from models.repo_model import Repository
from models.user_model import AuthorizedUserProfile, UserProfile
from schemas.commits_schema import LIST_COMMITS_SCHEMA
from schemas.user_schema import USER_PROFILE_SCHEMA, NEGATIVE_RESPONSE_SCHEMA
from utils.api_repos import get_commits_of_repository, get_commits_of_repository
from utils.schema_validator import validate_json_schema, from_dict


@pytest.mark.parametrize("repo_name", ["hello-world", "boysenberry-repo-1"])
@pytest.mark.smoke
def test_get_list_of_commits_of_octocat_contains_expected_fields(repo_name):
    with allure.step(
        f"Send GET request to fetch all the commits for repo'{repo_name}' for user octocat"
    ):
        response = get_commits_of_repository(owner="octocat", repo=repo_name)

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Validate JSON schema of the response contains all the data"):
        data = response.json()
        validate_json_schema(data, LIST_COMMITS_SCHEMA)

    with allure.step("Double check the needed keys"):
        for commit in data:
            commit_object = from_dict(commit, CommitDetail)
            assert commit_object.sha is not None
            assert commit_object.commit.author is not None
            assert commit_object.commit.message is not None
            assert commit_object.commit.committer.date is not None


@pytest.mark.parametrize("repo_name", ["hello-world", "boysenberry-repo-1"])
@pytest.mark.security
def test_test_get_list_of_commits_of_octocat_without_authorization(repo_name):
    with allure.step(
        f"Send GET request to fetch all the commits for repo'{repo_name}' for user octocat without authorization"
    ):
        response = get_commits_of_repository(
            owner="octocat", repo=repo_name, include_token=False
        )

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        validate_json_schema(data, LIST_COMMITS_SCHEMA)


@pytest.mark.parametrize("repo_name", ["hello-world", "boysenberry-repo-1"])
@pytest.mark.security
def test_get_list_of_commits_invalid_credentials(repo_name):
    with allure.step(
        f"Send GET request to fetch all the commits for repo'{repo_name}' for user octocat without authorization"
    ):
        response = get_commits_of_repository(
            owner="octocat", repo=repo_name, include_token=True, random_token=True
        )

    with allure.step("Validate the HTTP status code is 401 unauthorized"):
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    with allure.step(
        "Validate JSON schema of the response, that contains one more field called notification email"
    ):
        data = response.json()
        validate_json_schema(data, NEGATIVE_RESPONSE_SCHEMA)

    with allure.step("Check error message is the expected"):
        assert data["message"] == ErrorMessages.INVALID_CREDENTIALS


test_cases = [
    (1, 3, 3),
    (2, 3, 0),
]


@pytest.mark.parametrize("page, per_page, expected_count", test_cases)
def test_get_list_commits_of_user_octocat_pagination(page, per_page, expected_count):
    """
    octocat contains 3 commits in the hello world project
    """
    with allure.step(f"Send GET request to fetch user repositories - Page {page}"):
        response = get_commits_of_repository(
            "octocat", repo="hello-world", page=page, per_page=per_page
        )

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        validate_json_schema(data, LIST_COMMITS_SCHEMA)

    with allure.step(
        f"Check the number of commits in repo in page {page} is {expected_count}"
    ):
        assert (
            len(data) == expected_count
        ), f"Expected {expected_count}, got {len(data)}"


def test_get_list_commits_of_non_existent_user_or_repo():
    """
    octocat contains 3 commits in the hello world project
    """
    with allure.step(f"get commits of user octocatss ( invalid ) "):
        response = get_commits_of_repository("octocatss", repo="hello-world")

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    with allure.step(
        f"get commits of user octocat ( valid ) but hello-worlddd repo ( invalid "
    ):
        response = get_commits_of_repository("octocat", repo="hello-worldddddd")

    with allure.step("Validate the HTTP status code is 200"):
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


test_cases = [
    ("553c2077f0edc3d5dc5d17262f6aa498e69d6f8e", 200, 1),
    ("test-sha", 404, 0),
]


@pytest.mark.parametrize(("sha_value", "status_code", "number_commits"), test_cases)
def test_get_commits_with_sha_filter(sha_value, status_code, number_commits):
    """
    Test filtering repositories by 'SHA' query parameter commit 55...
    """
    with allure.step(f"Send GET request to fetch repositories of type"):
        response = get_commits_of_repository(
            "octocat", repo="hello-world", sha=sha_value, per_page=50
        )

    with allure.step("Validate the HTTP status code is 200"):
        assert (
            response.status_code == status_code
        ), f"Expected {status_code}, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        if status_code == 200:
            assert len(data) == number_commits


test_cases = [
    ("7fd1a60b01f91b314f59955a4e4d4e80d8edf11d", 200, 3),
    ("test-sha", 404, 0),
]


@pytest.mark.parametrize(("sha_value", "status_code", "number_commits"), test_cases)
def test_get_commits_with_sha_filter_branches_ahead(
    sha_value, status_code, number_commits
):
    """
    Test filtering repositories by 'SHA' query parameter. as sha 7f has oldest commit, will return everything
    """
    with allure.step(f"Send GET request to fetch repositories of type"):
        response = get_commits_of_repository(
            "octocat", repo="hello-world", sha=sha_value, per_page=50
        )

    with allure.step("Validate the HTTP status code is 200"):
        assert (
            response.status_code == status_code
        ), f"Expected {status_code}, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        if status_code == 200:
            assert len(data) == number_commits


def test_get_commits_filtering_by_file_path():
    """
    In this case we will use this exact project to test it. As the commits are increasing, we will check that
    at least, that filtering by conftest file path has less commits than without filtering, in this case,
    we will be sure we will have more commits.
    """
    with allure.step(f"Send GET request to fetch repositories of type"):
        response = get_commits_of_repository(
            "aleixbernardo", repo="github_testing", path="", per_page=50
        )

    with allure.step("Validate the HTTP status code is 200"):
        assert (
            response.status_code == 200
        ), f"Expected {200}, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        non_filtered_commits = len(data)

    with allure.step(f"Send GET request to fetch repositories of type"):
        response = get_commits_of_repository(
            "aleixbernardo", repo="github_testing", path="conftest.py", per_page=50
        )

    with allure.step("Validate the HTTP status code is 200"):
        assert (
            response.status_code == 200
        ), f"Expected {200}, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()
        filtered_commits = len(data)

    with allure.step("Check the filtered commits < non_filtered_commits"):
        assert filtered_commits < non_filtered_commits


@pytest.mark.parametrize("committer", ["octocat", "Spaceghost", "Cameron423698"])
def test_get_commits_filtering_by_committer(committer):
    """
    In the cotocat - hello world project, we have 3 commits, 1 made by The Octocat, 1 made by Johnneylee Jack Rollins
    and one made by cameronmcefee
    """
    with allure.step(f"Send GET request to fetch repositories of type"):
        response = get_commits_of_repository(
            "octocat", repo="hello-world", committer=committer, per_page=50
        )

    with allure.step("Validate the HTTP status code is 200"):
        assert (
            response.status_code == 200
        ), f"Expected {200}, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()

    with allure.step("Create object"):
        commit_objects = [from_dict(commit, CommitDetail) for commit in data]

    with allure.step("Check commits"):
        assert len(data) == 1
        assert all(
            [commit.committer["login"] == committer for commit in commit_objects]
        )


@pytest.mark.parametrize("author", ["octocat", "Spaceghost", "Cameron423698"])
def test_get_commits_filtering_by_author(author):
    """
    In the cotocat - hello world project, we have 3 commits, 1 made by The Octocat, 1 made by Johnneylee Jack Rollins
    and one made by cameronmcefee
    """
    with allure.step(f"Send GET request to fetch repositories of type"):
        response = get_commits_of_repository(
            "octocat", repo="hello-world", author=author, per_page=50
        )

    with allure.step("Validate the HTTP status code is 200"):
        assert (
            response.status_code == 200
        ), f"Expected {200}, got {response.status_code}"

    with allure.step("Validate JSON schema of the response"):
        data = response.json()

    with allure.step("Create object"):
        commit_objects = [from_dict(commit, CommitDetail) for commit in data]

    with allure.step("Check commits"):
        assert len(data) == 1
        assert all([commit.author["login"] == author for commit in commit_objects])


test_filter_cases = [
    ("2011-09-14T03:42:41Z", 2),  # Expecting 2 commits since that date
    ("2022-09-20T15:41:52Z", 0),  # Expecting 0 commits since this date
]


@pytest.mark.parametrize("since_value, number_commits", test_filter_cases)
def test_get_commits_since_date(since_value, number_commits):
    """
    The dates of the commits are :
       2012-03-06T23:06:50Z
       2011-09-14T04:42:41Z
       2011-01-26T19:06:08Z
    """
    with allure.step(f"Send GET request to fetch commits since {since_value}"):
        response = get_commits_of_repository(
            "octocat", repo="hello-world", since=since_value, per_page=50
        )
        data = response.json()

    with allure.step(f"Convert JSON response to list of Commit objects"):
        commits_obj = [from_dict(commit, CommitDetail) for commit in data]
        assert (
            len(commits_obj) == number_commits
        ), f"Expected {number_commits} commits but got {len(commits_obj)}"

    with allure.step(f"Check all commit dates are after {since_value}"):
        before_value_dt = datetime.strptime(since_value, "%Y-%m-%dT%H:%M:%SZ")
        for commit in commits_obj:
            # Use the committer date, or the author date if needed
            commit_date_dt = datetime.strptime(
                commit.commit.committer.date, "%Y-%m-%dT%H:%M:%SZ"
            )
            assert (
                commit_date_dt >= before_value_dt
            ), f"Commit date {commit.commit.committer.date} is before {since_value}. Commit SHA: {commit.sha}"


test_filter_cases_until = [
    ("2011-09-14T05:42:41Z", 2),  # Expecting 1 commit before this date
    ("2022-09-20T23:07:52Z", 3),
    # Expecting 3 commits before this date (since the test dataset includes earlier commits)
]


@pytest.mark.parametrize("until_value, number_commits", test_filter_cases_until)
def test_get_commits_until_date(until_value, number_commits):
    """
    The dates of the commits are :
       2012-03-06T23:06:50Z
       2011-09-14T04:42:41Z
       2011-01-26T19:06:08Z
    """
    with allure.step(f"Send GET request to fetch commits until {until_value}"):
        response = get_commits_of_repository(
            "octocat", repo="hello-world", until=until_value, per_page=50
        )
        data = response.json()

    with allure.step(f"Convert JSON response to list of Commit objects"):
        commits_obj = [from_dict(commit, CommitDetail) for commit in data]
        assert (
            len(commits_obj) == number_commits
        ), f"Expected {number_commits} commits but got {len(commits_obj)}"

    with allure.step(f"Check all commit dates are before {until_value}"):
        until_value_dt = datetime.strptime(until_value, "%Y-%m-%dT%H:%M:%SZ")
        for commit in commits_obj:
            # Use the committer date, or the author date if needed
            commit_date_dt = datetime.strptime(
                commit.commit.committer.date, "%Y-%m-%dT%H:%M:%SZ"
            )
            assert (
                commit_date_dt <= until_value_dt
            ), f"Commit date {commit.commit.committer.date} is after {until_value}. Commit SHA: {commit.sha}"


# Define corner case invalid timestamps (before and after Git's acceptable range)
invalid_dates = [
    (
        "1969-12-31T23:59:59Z",
        "Date is before the Unix epoch (1970-01-01)",
    ),  # Before Unix epoch
    (
        "2100-01-01T00:00:00Z",
        "Date is after the maximum allowed date (2099-12-31)",
    ),  # After the maximum allowed date
]


@pytest.mark.parametrize("invalid_date, expected_error_message", invalid_dates)
def test_invalid_timestamp_handling(invalid_date, expected_error_message):
    """
    Test handling of invalid timestamps. The allowed range is:
      - From 1970-01-01T00:00:00Z (Unix epoch)
      - Until 2099-12-31T23:59:59Z
    """
    with allure.step(f"Send GET request with invalid timestamp {invalid_date}"):
        response = get_commits_of_repository(
            "octocat",
            repo="hello-world",
            since=invalid_date,
            until=invalid_dates,
            per_page=50,
        )
        data = response.json()

    with allure.step("Check error status code"):
        assert response.status_code == 400


# Define invalid combinations of `since` and `until` dates
invalid_date_combinations = [
    # since is later than until
    (
        "2022-09-20T15:41:52Z",
        "2022-09-19T15:41:52Z",
        "The 'since' date must be earlier than the 'until' date",
    ),
    # since date is out of range
    (
        "1969-12-31T23:59:59Z",
        "2025-01-01T00:00:00Z",
        "The 'since' date is before the Unix epoch (1970-01-01)",
    ),
    # until date is out of range
    (
        "2022-01-01T00:00:00Z",
        "2100-01-01T00:00:00Z",
        "The 'until' date is after the maximum allowed date (2099-12-31)",
    ),
    # both since and until are out of range
    (
        "1969-12-31T23:59:59Z",
        "2100-01-01T00:00:00Z",
        "Both 'since' and 'until' dates are out of valid range",
    ),
]


@pytest.mark.parametrize(
    "since_date, until_date, expected_error_message", invalid_date_combinations
)
def test_invalid_since_until_combination(
    since_date, until_date, expected_error_message
):
    """
    Test invalid combinations of `since` and `until` dates.
    - `since` > `until`
    - `since` or `until` out of Git's acceptable range.
    """
    with allure.step(
        f"Send GET request with invalid date combination - since: {since_date}, until: {until_date}"
    ):
        # Try to send a GET request with the given invalid dates
        response = get_commits_of_repository(
            "octocat",
            repo="hello-world",
            since=since_date,
            until=until_date,
            per_page=50,
        )

    with allure.step("Check error status code"):
        assert response.status_code == 400
