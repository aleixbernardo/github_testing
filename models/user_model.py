from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class UserProfile:
    login: str
    id: int
    node_id: str
    avatar_url: str
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
    gravatar_id: Optional[str] = None  # Can be an empty string
    name: Optional[str] = None
    company: Optional[str] = None
    blog: Optional[str] = None  # Can be an empty string
    location: Optional[str] = None
    email: Optional[str] = None
    hireable: Optional[bool] = None
    bio: Optional[str] = None
    twitter_username: Optional[str] = None
    public_repos: int = 0
    public_gists: int = 0
    followers: int = 0
    following: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None  # Add default for missing field


@dataclass
class AuthorizedUserProfile(UserProfile):
    # Private fields (only available when authenticated)
    private_gists: Optional[int] = None
    total_private_repos: Optional[int] = None
    owned_private_repos: Optional[int] = None
    disk_usage: Optional[int] = None
    collaborators: Optional[int] = None
    two_factor_authentication: Optional[bool] = None
    plan: Optional[Dict] = None  # The 'plan' field is an object, so use dict
    notification_email: Optional[str] = None
