from dataclasses import dataclass
from typing import List, Optional

from models.user_model import UserProfile


@dataclass
class Tree:
    url: str
    sha: str


@dataclass
class Verification:
    verified: bool
    reason: str
    signature: Optional[str]
    payload: Optional[str]
    verified_at: Optional[str]


@dataclass
class CommitInfo:
    name: str
    email: str
    date: str


@dataclass
class Commit:
    url: str
    author: CommitInfo
    committer: CommitInfo
    message: str
    tree: Tree
    comment_count: int
    verification: Verification


@dataclass
class Parent:
    url: str
    html_url: str
    sha: str


@dataclass
class CommitDetail:
    url: str
    sha: str
    node_id: str
    html_url: str
    comments_url: str
    commit: Commit
    author: Optional[UserProfile]
    committer: Optional[UserProfile]
    parents: List[Parent]
