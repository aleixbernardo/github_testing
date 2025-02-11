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
from utils.api_repos import get_commits_of_repository
from utils.schema_validator import validate_json_schema, from_dict

@pytest.mark.epic('GitHub API')
@pytest.mark.feature('GitHub Commits')
class TestGitHubCommits:
    @pytest.mark.parametrize("repo_name", ["hello-world", "boysenberry-repo-1"])
    @pytest.mark.smoke
    @pytest.mark.story('Get List of Commits Response Fields')
    def test_get_list_of_commits_contains_expected_fields(self, repo_name):
        response = get_commits_of_repository(owner="octocat", repo=repo_name)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        validate_json_schema(data, LIST_COMMITS_SCHEMA)

        for commit in data:
            commit_object = from_dict(commit, CommitDetail)
            assert commit_object.sha
            assert commit_object.commit.author
            assert commit_object.commit.message
            assert commit_object.commit.committer.date

    @pytest.mark.parametrize("repo_name", ["hello-world", "boysenberry-repo-1"])
    @pytest.mark.security
    @pytest.mark.story('Get List of Commits Without Authorization')

    def test_get_list_of_commits_without_authorization(self, repo_name):
        response = get_commits_of_repository(owner="octocat", repo=repo_name, include_token=False)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        validate_json_schema(data, LIST_COMMITS_SCHEMA)

    @pytest.mark.parametrize("repo_name", ["hello-world", "boysenberry-repo-1"])
    @pytest.mark.security
    @pytest.mark.story('Get List of Commits Invalid Credentials')

    def test_get_list_of_commits_invalid_credentials(self, repo_name):
        response = get_commits_of_repository(
            owner="octocat", repo=repo_name, include_token=True, random_token=True
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

        data = response.json()
        validate_json_schema(data, NEGATIVE_RESPONSE_SCHEMA)

        assert data["message"] == ErrorMessages.INVALID_CREDENTIALS

    @pytest.mark.parametrize("page, per_page, expected_count", [(1, 3, 3), (2, 3, 0)])
    @pytest.mark.story('Get List of Commits Paginated')

    def test_get_list_commits_pagination(self, page, per_page, expected_count):
        response = get_commits_of_repository("octocat", repo="hello-world", page=page, per_page=per_page)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        validate_json_schema(data, LIST_COMMITS_SCHEMA)

        assert len(data) == expected_count, f"Expected {expected_count}, got {len(data)}"
    @pytest.mark.story('Get List of Commits Non existent User or Repo')

    def test_get_list_commits_non_existent_user_or_repo(self):
        response = get_commits_of_repository("octocatss", repo="hello-world")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

        response = get_commits_of_repository("octocat", repo="hello-worldddddd")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    @pytest.mark.parametrize(
        "sha_value, status_code, number_commits",
        [("553c2077f0edc3d5dc5d17262f6aa498e69d6f8e", 200, 1), ("test-sha", 404, 0)],
    )
    @pytest.mark.story('Get List of Commits Filtering by SHA')

    def test_get_commits_with_sha_filter(self, sha_value, status_code, number_commits):
        response = get_commits_of_repository("octocat", repo="hello-world", sha=sha_value, per_page=50)

        assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}"

        data = response.json()
        if status_code == 200:
            assert len(data) == number_commits

    @pytest.mark.parametrize("committer", ["octocat", "Spaceghost", "Cameron423698"])
    @pytest.mark.story('Get List of Commits Filtering by committer')

    def test_get_commits_filtering_by_committer(self, committer):
        response = get_commits_of_repository("octocat", repo="hello-world", committer=committer, per_page=50)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        commit_objects = [from_dict(commit, CommitDetail) for commit in data]

        assert len(data) == 1
        assert all(commit.committer["login"] == committer for commit in commit_objects)

    @pytest.mark.parametrize("author", ["octocat", "Spaceghost", "Cameron423698"])
    @pytest.mark.story('Get List of Commits Filtering by Author')

    def test_get_commits_filtering_by_author(self, author):
        response = get_commits_of_repository("octocat", repo="hello-world", author=author, per_page=50)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        commit_objects = [from_dict(commit, CommitDetail) for commit in data]

        assert len(data) == 1
        assert all(commit.author["login"] == author for commit in commit_objects)

    @pytest.mark.parametrize(
        "since_value, number_commits",
        [("2011-09-14T03:42:41Z", 2), ("2022-09-20T15:41:52Z", 0)],
    )
    @pytest.mark.story('Get List of Commits Filtering by Since date')

    def test_get_commits_since_date(self, since_value, number_commits):
        response = get_commits_of_repository("octocat", repo="hello-world", since=since_value, per_page=50)
        data = response.json()

        commits_obj = [from_dict(commit, CommitDetail) for commit in data]
        assert len(commits_obj) == number_commits

        before_value_dt = datetime.strptime(since_value, "%Y-%m-%dT%H:%M:%SZ")
        for commit in commits_obj:
            commit_date_dt = datetime.strptime(commit.commit.committer.date, "%Y-%m-%dT%H:%M:%SZ")
            assert commit_date_dt >= before_value_dt

    @pytest.mark.parametrize(
        "invalid_date, expected_error_message",
        [
            ("1969-12-31T23:59:59Z", "Date is before the Unix epoch (1970-01-01)"),
            ("2100-01-01T00:00:00Z", "Date is after the maximum allowed date (2099-12-31)"),
        ],
    )
    @pytest.mark.story('Get List of Commits Invalid TimeStamp Handling')

    def test_invalid_timestamp_handling(self, invalid_date, expected_error_message):
        response = get_commits_of_repository("octocat", repo="hello-world", since=invalid_date, per_page=50)
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "since_date, until_date, expected_error_message",
        [
            ("2022-09-20T15:41:52Z", "2022-09-19T15:41:52Z", "The 'since' date must be earlier than the 'until' date"),
            ("1969-12-31T23:59:59Z", "2025-01-01T00:00:00Z", "The 'since' date is before the Unix epoch (1970-01-01)"),
            ("2022-01-01T00:00:00Z", "2100-01-01T00:00:00Z", "The 'until' date is after the maximum allowed date"),
        ],
    )
    @pytest.mark.story('Get List of Commits Invalid TimeStamp Handling')

    def test_invalid_since_until_combination(self, since_date, until_date, expected_error_message):
        response = get_commits_of_repository("octocat", repo="hello-world", since=since_date, until=until_date, per_page=50)
        assert response.status_code == 400
