# GitHub Testing

## Setup Instructions

### 1. Generate a GitHub API Token

To authenticate correctly with the GitHub API, follow these steps:

1. Go to [GitHub Personal Access Tokens](https://github.com/settings/tokens).
2. Click **"Generate new token"** (select the **Classic** option for general use).
3. Select the **repo** and **user** scopes.
4. Generate the token and copy it.
5. Create a `.env` file in the project root and add:
   ```plaintext
   GITHUB_TOKEN=your_generated_token

### 2. Install dependencies

Run the following command to install the required dependencies:

   ```plaintext
   pip install -r requirements.txt
   ```

### Reporting

After each test run, a fresh new folder is generated in  the root folder called allure-results with all test data, steps and screenshots,
thanks to the pytest ini configuration.
To see the allure report in local, just run
```plaintext
   allure serve allure-results
   ```

### Code Formatting

The formatting library chosen for this project is black ( installed in requirements.txt)
Once it is installed, just run black . in the terminal or follow the next site to set the file watcher to do it
automatically in every change
https://akshay-jain.medium.com/pycharm-black-with-formatting-on-auto-save-4797972cf5de

### API Schema

The JSON schemas used in this project are based on the official GitHub API documentation:
https://docs.github.com/en/rest/users/users?apiVersion=2022-11-28

### Pipeline

Pipeline is found in https://github.com/aleixbernardo/github_testing/actions to trigger manually with the
personal github token as parameter.


### Important Notes

1. There is a rate limit for unauthenticated API requests. Don't run the unauthenticated tests a lot of times or you
   will get eventually a 403
2. Store your .env file securely and do not commit it to version control.

### Comments
1. During the testing development, I realised that there are some erors in the status code responses for some endpoints, and some errors in the dates, as found in the test fails.
2. Parametrization has not been implemented because the list of tests is small, and the API responses are fast, making it unnecessary.