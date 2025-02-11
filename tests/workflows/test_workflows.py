import pytest
import allure

from models.commit_model import CommitDetail
from models.repo_model import Repository
from models.user_model import AuthorizedUserProfile
from schemas.commits_schema import LIST_COMMITS_SCHEMA
from schemas.repos_schema import LIST_REPOSITORIES_SCHEMA
from utils.api_repos import get_repositories_from_logged_user, get_commits_of_repository
from utils.api_users import get_logged_user_profile, update_user_profile
from utils.schema_validator import validate_json_schema, from_dict


@pytest.mark.smoke
def test_github_api_workflow(reset_github_profile_attributes):
    """
    This test simulates a full API workflow:
    1. Try to fetch user profile without a token (401)
    2. Fetch user profile with a valid token (200)
    3. Update user profile (PATCH)
    4. Validate profile update (GET)
    5. Fetch user repositories (GET)
    6. Attempt to fetch commits for a non-existent repo (404)
    7. Fetch commits from the first repo
    8. Fetch commits from the last repo
    """

    with allure.step(
        "Step 1: Try to retrieve the user's profile without a Bearer token and validate that access is denied"
    ):
        response = get_logged_user_profile(include_token=False)
        assert response.status_code == 401, f"Expected 200, got {response.status_code}"

    with allure.step(
        "Step 2: Set the Bearer token and retry fetching the profile, this time validating that access is granted"
    ):
        response = get_logged_user_profile(include_token=True)
        assert (
            response.status_code == 200
        ), f"Expected 200, but got {response.status_code}"
        user_profile = AuthorizedUserProfile(**response.json())
        assert user_profile.name == "aleix"

    with allure.step(
        "Step 3: Update a field in the logged-in user’s profile, such as the bio or name"
    ):
        new_name = "This is the new name."
        response = update_user_profile({"name": new_name})
        assert (
            response.status_code == 200
        ), f"Expected 200, but got {response.status_code}"

    with allure.step(
        "Step 4: Retrieve the profile again and validate that the field has been successfully updated."
    ):
        response = get_logged_user_profile(include_token=True)
        assert (
            response.status_code == 200
        ), f"Expected 200, but got {response.status_code}"
        new_user_profile = AuthorizedUserProfile(**response.json())
        assert new_user_profile.name == new_name

    with allure.step(
        "Step 5: Obtain the list of repositories for the logged-in user (both public and private. Ensure that the repositories are listed correctly"
    ):
        response = get_repositories_from_logged_user()
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        repo_objects = [from_dict(repo, Repository) for repo in response.json()]

        assert len(repo_objects) == 9
        assert all([repo.owner.login == "aleixbernardo"] for repo in repo_objects)
        github_testing_repo = next(
            (repo for repo in repo_objects if repo.name == "github_testing")
        )
        assert github_testing_repo.private is False

        github_testing_repo = next(
            (repo for repo in repo_objects if repo.name == "travel_planner")
        )
        assert github_testing_repo.private is True

        validate_json_schema(response.json(), LIST_REPOSITORIES_SCHEMA)

    with allure.step(
        "Step 6: Attempt to list commits for a non-existent repository and validate that the appropriate error is returned"
    ):
        response = get_commits_of_repository("aleixbernardo", repo="hello-world")
        assert response.status_code == 404

    with allure.step(
        "Step 7: List commits from the first repository of the logged-in user and validate the key fields (sha, author, message, date) in the response"
    ):
        first_repo_name = repo_objects[0].name
        first_repo_owner = repo_objects[0].owner.login
        last_repo_name = repo_objects[-1].name
        last_repo_owner = repo_objects[-1].owner.login

        response = get_commits_of_repository(first_repo_owner, repo=first_repo_name)

        assert response.status_code == 200
        commit_objects = [from_dict(commit, CommitDetail) for commit in response.json()]

        for commit in commit_objects:
            assert commit.sha is not None
            assert commit.commit.author.name == "aleixbernardo"
            assert commit.commit.author.date is not None

    with allure.step("Step 8: Fetch commits from the last repository"):
        response = get_commits_of_repository(last_repo_owner, repo=last_repo_name)

        assert response.status_code == 200
        commit_objects = [from_dict(commit, CommitDetail) for commit in response.json()]

        for commit in commit_objects:
            assert commit.sha is not None
            assert commit.commit.author.name == "mbernardo95" or "Marc Bernardo Ferré"
            assert commit.commit.author.date is not None
