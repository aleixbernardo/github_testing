import pytest
import allure

@pytest.mark.smoke
def test_github_workflow():
    # Step 1: Try to retrieve the user's profile without a Bearer token and validate that access is denied (401 Unauthorized).
    with allure.step("Step 1: Attempt to fetch the user's profile without a token"):
        url = f"{base_url}/user"
        response = requests.get(url)

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    # Step 2: Set the Bearer token and retry fetching the profile, validating that access is granted (200 OK).
    with allure.step("Step 2: Fetch the user's profile with Bearer token"):
        response = requests.get(url, headers=headers)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        user_data = response.json()
        assert "login" in user_data, "Login is not present in the response"

    # Step 3: Update a field in the logged-in user’s profile (e.g., bio).
    with allure.step("Step 3: Update the user's bio"):
        payload = {"bio": "This is the updated bio!"}
        response = requests.patch(url, headers=headers, json=payload)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        updated_user_data = response.json()
        assert updated_user_data.get("bio") == payload[
            "bio"], f"Expected bio to be '{payload['bio']}', but got {updated_user_data.get('bio')}"

    # Step 4: Retrieve the profile again and validate that the field has been successfully updated.
    with allure.step("Step 4: Retrieve the updated profile and verify the bio"):
        response = requests.get(url, headers=headers)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        user_data = response.json()
        assert user_data.get("bio") == "This is the updated bio!", "Bio was not updated correctly"

    # Step 5: Obtain the list of repositories for the logged-in user (both public and private).
    with allure.step("Step 5: List the user's repositories"):
        repos_url = f"{base_url}/user/repos"
        response = requests.get(repos_url, headers=headers)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        repos = response.json()
        assert isinstance(repos, list), "Expected a list of repositories"
        assert len(repos) > 0, "No repositories found"

    # Step 6: Attempt to list commits for a non-existent repository and validate the appropriate error (404 Not Found).
    with allure.step("Step 6: Attempt to list commits from a non-existent repository"):
        invalid_repo_url = f"{base_url}/repos/{os.getenv('GITHUB_USERNAME')}/non_existent_repo/commits"
        response = requests.get(invalid_repo_url, headers=headers)

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    # Step 7: List commits from the first repository of the logged-in user and validate key fields (sha, author, message, date).
    with allure.step("Step 7: List commits from the first repository"):
        first_repo = repos[0]
        commits_url = f"{base_url}/repos/{first_repo['owner']['login']}/{first_repo['name']}/commits"
        response = requests.get(commits_url, headers=headers)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        commits = response.json()
        assert len(commits) > 0, "No commits found"

        for commit in commits:
            assert "sha" in commit, "Commit sha is missing"
            assert "commit" in commit, "Commit message is missing"
            assert "author" in commit["commit"], "Commit author is missing"
            assert "date" in commit["commit"]["author"], "Commit date is missing"

    # Step 8: List commits from the last repository of the logged-in user and validate key fields.
    with allure.step("Step 8: List commits from the last repository"):
        last_repo = repos[-1]
        commits_url = f"{base_url}/repos/{last_repo['owner']['login']}/{last_repo['name']}/commits"
        response = requests.get(commits_url, headers=headers)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        commits = response.json()
        assert len(commits) > 0, "No commits found"

        for commit in commits:
            assert "sha" in commit, "Commit sha is missing"
            assert "commit" in commit, "Commit message is missing"
            assert "author" in commit["commit"], "Commit author is missing"
            assert "date" in commit["commit"]["author"], "Commit date is missing"