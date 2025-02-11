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

### Code Formatting

The formatting library chosen for this project is black ( installed in requirements.txt)
Once it is installed, just run black . in the terminal or follow the next site to set the file watcher to do it
automatically in every change
https://akshay-jain.medium.com/pycharm-black-with-formatting-on-auto-save-4797972cf5de

### API Schema

The JSON schemas used in this project are based on the official GitHub API documentation:
https://docs.github.com/en/rest/users/users?apiVersion=2022-11-28

### Important Notes

1. There is a rate limit for unauthenticated API requests. Don't run the unauthenticated tests a lot of times or you
   will get eventually a 403
2. Store your .env file securely and do not commit it to version control.
