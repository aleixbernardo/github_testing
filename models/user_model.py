from dataclasses import dataclass
from typing import Optional

@dataclass
class UserProfile:
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: Optional[str]  # Can be an empty string
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    user_view_type: str  # Newly added field
    site_admin: bool
    name: Optional[str]
    company: Optional[str]
    blog: Optional[str]  # Can be an empty string
    location: Optional[str]
    email: Optional[str]
    hireable: Optional[bool]
    bio: Optional[str]
    twitter_username: Optional[str]
    public_repos: int
    public_gists: int
    followers: int
    following: int
    created_at: str
    updated_at: str
