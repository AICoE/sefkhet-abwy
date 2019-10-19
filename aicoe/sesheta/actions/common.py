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
import typing
import base64
import re

import gidgethub

from functools import wraps
from itertools import takewhile

from octomachinery.github.api.tokens import GitHubOAuthToken
from octomachinery.github.api.raw_client import RawGitHubAPI
from octomachinery.app.runtime.context import RUNTIME_CONTEXT
from codeowners import CodeOwners

from thoth.common import init_logging


init_logging()

_LOGGER = logging.getLogger(__name__)


def cocommand(f):
    """Based on https://github.com/pallets/click/issues/85 ."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


def unpack(s):
    """Unpack a list into a string.

    see https://stackoverflow.com/questions/42756537/f-string-syntax-for-unpacking-a-list-with-brace-suppression
    """
    return " ".join(map(str, s))  # map(), just for kicks


async def conclude_reviewer_list(owner: str = None, repo: str = None) -> typing.List[str]:
    """Conclude on a set of Reviewers (their GitHub user id) that could be assigned to a Pull Request."""
    reviewers = []
    github_api = None

    if owner is None or repo is None:
        return None

    try:
        github_api = RUNTIME_CONTEXT.app_installation_client
    except Exception:
        access_token = GitHubOAuthToken(os.environ["GITHUB_ACCESS_TOKEN"])
        github_api = RawGitHubAPI(access_token, user_agent="sesheta-actions")

    try:
        codeowners = await github_api.getitem(f"/repos/{owner}/{repo}/contents/.github/CODEOWNERS")
        codeowners_content = base64.b64decode(codeowners["content"]).decode("utf-8")

        code_owner = CodeOwners(codeowners_content)
        for owner in code_owner.of("."):
            reviewers.append(owner[1][1:])  # remove the @

    except gidgethub.HTTPException as http_exception:  # if there is no CODEOWNERS, lets have some sane defaults
        if http_exception.status_code == 404:
            if owner.lower() == "thoth-station":
                reviewers.append("fridex")
                reviewers.append("pacospace")
            if "prometheus" in repo.lower():
                reviewers.append("4n4nd")
                reviewers.append("MichaelClifford")
            if "log-" in repo.lower():
                reviewers.append("zmhassan")
                reviewers.append("4n4nd")
        else:
            _LOGGER.error(http_exception)
            return None

    except Exception as err:  # on any other Error, we can not generate a reviewers list
        _LOGGER.error(str(err))
        return None

    _LOGGER.debug(f"final reviewers: '{reviewers}'")

    return reviewers


async def get_master_head_sha(owner: str, repo: str) -> str:
    """Get the SHA of the HEAD of the master."""
    # TODO refactor this to a class? global variable?
    access_token = GitHubOAuthToken(os.environ["GITHUB_ACCESS_TOKEN"])
    github_api = RawGitHubAPI(access_token, user_agent="sesheta-actions")
    commits = await github_api.getitem(f"/repos/{owner}/{repo}/commits")

    _LOGGER.debug(f"HEAD commit of {owner}/{repo}: {commits[0]}")

    return commits[0]["sha"]  # FIXME could raise IndexError


async def get_pull_request(owner: str, repo: str, pull_request: int) -> dict:
    """Get PR from owner/repo."""
    access_token = GitHubOAuthToken(os.environ["GITHUB_ACCESS_TOKEN"])
    github_api = RawGitHubAPI(access_token, user_agent="sesheta-actions")

    pr = await github_api.getitem(f"/repos/{owner}/{repo}/pulls/{pull_request}")  # TODO exception handling

    _LOGGER.debug(f"{owner}/{repo}: PR {pull_request}: {pr}")

    return pr


async def trigger_update_branch(owner: str, repo: str, pull_request: int) -> bool:
    """Trigger /update-branch API on Pull Request."""
    access_token = GitHubOAuthToken(os.environ["GITHUB_ACCESS_TOKEN"])
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
