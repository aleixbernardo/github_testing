import logging
import shutil
import os
import pytest
from dotenv import load_dotenv

from utils.api_users import update_user_profile

ALLURE_RESULTS_DIR = "allure-results"

# Load variables from .env file
load_dotenv()


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


@pytest.fixture(scope="function", autouse=False)
def reset_github_attributes():
    """
    This fixture will reset github user attributes like the name when called. Needed to setup the particular
    test in which we update the attributes
    """
    logging.info("Resetting the aleixbernardo attributes")
    update_user_profile({"name": "aleix"})
    yield
