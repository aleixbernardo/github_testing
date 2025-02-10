import requests

BASE_URL = "https://api.github.com/users"

def get_user_profile(username: str):
    """ Get the public profile of a username """
    url = f"{BASE_URL}/{username}"
    response = requests.get(url)
    return response