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

import logging

import gidgethub

from octomachinery.github.api.tokens import GitHubOAuthToken
from octomachinery.github.api.raw_client import RawGitHubAPI

from aicoe.sesheta.actions.common import get_master_head_sha, get_pull_request, trigger_update_branch

from thoth.common import init_logging


_LOGGER = logging.getLogger("pull_request")
_LOGGER.setLevel(logging.DEBUG)


async def merge_master_into_pullrequest(
    owner: str, repo: str, pull_request: int, token: str = None, dry_run: bool = False
) -> bool:
    """Merge the master branch into the Pull Request."""
    triggered = True

    head_sha = await get_master_head_sha(owner, repo)
    _r = await get_pull_request(owner, repo, pull_request)

    # FIXME chk if PR exists, if not return

    rebaseable = _r["rebaseable"]
    base_sha = _r["base"]["sha"]

    # TODO if rebaseable is None, we need to come back in a few seconds, github has not finished a background task
    if rebaseable and (base_sha != head_sha):
        _LOGGER.info(
            f"rebasing Pull Request {pull_request} in {owner}/{repo} into master"
            f", head sha = {head_sha} and pull requests's base sha = {base_sha}"
        )
        if not dry_run:
            triggered = await trigger_update_branch(owner, repo, pull_request)

        else:
            _LOGGER.info("just a dry-run...")
    else:
        _LOGGER.info(f"not triggering a rebase, head sha = {head_sha} and pull requests's base sha = {base_sha}")

    return triggered


if __name__ == "__main__":
    pass
