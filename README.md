# github_testing



1 - To get the token for correct authentification of the GITHUB API, go to :
https://github.com/settings/tokens
2 - Generate a new token with (classic) option, general use
3- Select repo and users checkbox
4 - Save it and copy it in a .env file (saved in the root) as GITHUB_TOKEN = xxxxxxxx
5 - PIp install -r requirements.txt


the json schemas are retrieved from the official github api documentation https://docs.github.com/en/rest/users/users?apiVersion=2022-11-28
