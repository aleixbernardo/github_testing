import shutil
import os
import pytest

ALLURE_RESULTS_DIR = "allure-results"

@pytest.fixture(scope="session", autouse=True)
def clean_allure_results():
    """
        This fixture automatically runs once per test session before any tests execute.
        It checks if the 'allure-results' directory exists and, if so, deletes it to ensure
        that old test results are removed. Then, it recreates the directory so that new results
        can be generated cleanly.
        """

    if os.path.exists(ALLURE_RESULTS_DIR):
        shutil.rmtree(ALLURE_RESULTS_DIR)
    os.makedirs(ALLURE_RESULTS_DIR)
