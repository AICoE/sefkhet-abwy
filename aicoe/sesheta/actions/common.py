#!/usr/bin/env python3
# sesheta-actions
# Copyright(C) 2019 Christoph Görn
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Sesheta's actions."""


import asyncio
import os
import logging

import gidgethub

from functools import wraps

from octomachinery.github.api.tokens import GitHubOAuthToken
from octomachinery.github.api.raw_client import RawGitHubAPI


_LOGGER = logging.getLogger(__name__)


def cocommand(f):
    """Based on https://github.com/pallets/click/issues/85 ."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


async def get_master_head_sha(owner: str, repo: str) -> str:
    # TODO refactor this to a class? global variable?
    access_token = GitHubOAuthToken(os.environ["SESHETA_ACTION_GITHUB_ACCESS_TOKEN"])
    github_api = RawGitHubAPI(access_token, user_agent="sesheta")
    commits = await github_api.getitem(f"/repos/{owner}/{repo}/commits")

    _LOGGER.debug(f"HEAD commit of {owner}/{repo}: {commits[0]}")

    return commits[0]["sha"]  # FIXME could raise IndexError


async def get_pull_request(owner: str, repo: str, pull_request: int) -> dict:
    """Get PR from owner/repo."""
    access_token = GitHubOAuthToken(os.environ["SESHETA_ACTION_GITHUB_ACCESS_TOKEN"])
    github_api = RawGitHubAPI(access_token, user_agent="sesheta")

    pr = await github_api.getitem(f"/repos/{owner}/{repo}/pulls/{pull_request}")

    _LOGGER.debug(f"{owner}/{repo}: PR {pull_request}: {pr}")

    return pr


async def trigger_update_branch(owner: str, repo: str, pull_request: int) -> bool:
    """Trigger /update-branch API on Pull Request."""
    access_token = GitHubOAuthToken(os.environ["SESHETA_ACTION_GITHUB_ACCESS_TOKEN"])
    github_api = RawGitHubAPI(access_token, user_agent="sesheta")

    try:
        if github_api.is_initialized:
            triggered = await github_api.put(
                f"/repos/{owner}/{repo}/pulls/{pull_request}/update-branch", preview_api_version="lydian", data=b""
            )

        _LOGGER.debug(f"rebasing Pull Request {pull_request} in {owner}/{repo} triggered: {triggered}")
        return True
    except gidgethub.BadRequest as bad_request:
        _LOGGER.error(f"{bad_request}: on /repos/{owner}/{repo}/pulls/{pull_request}/update-branch")
        return False
    except gidgethub.HTTPException as http_exception:
        if http_exception.status_code == 202:
            return True
        else:
            _LOGGER.error(http_exception)
            return False
