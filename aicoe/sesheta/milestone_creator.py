#!/usr/bin/env python3
# Sesheta
# Copyright(C) 2019,2020 Christoph Görn
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


"""This will normalize some standard labels."""


import os
import asyncio
import logging
import time

from datetime import datetime

import aiohttp

from octomachinery.github.api.tokens import GitHubOAuthToken
from octomachinery.github.api.raw_client import RawGitHubAPI

from thoth.common import init_logging
from aicoe.sesheta import __version__
from aicoe.sesheta.actions.label import (
    DEFAULT_LABELS,
    DEFAULT_MILESTONES_THOTH,
    create_or_update_label,
    create_or_update_milestone,
)


init_logging(logging_env_var_start="SEFKHET__ABWY_LOG_")

_LOGGER = logging.getLogger("thoth.labelnormalizer")
_LOGGER.setLevel(logging.DEBUG if bool(int(os.getenv("DEBUG", 0))) else logging.INFO)

_LOGGER.info(f"Sesheta action: milestone_creator, Version v{__version__}")
_LOGGER.debug(f"DEBUG mode is enabled")


async def update_milestones(org: str = "thoth-station"):
    """Update Milestones for one org."""
    access_token = GitHubOAuthToken(os.environ["GITHUB_ACCESS_TOKEN"])

    async with aiohttp.ClientSession() as client:
        github_api = RawGitHubAPI(access_token, session=client, user_agent="sesheta-actions")

        async for repo in github_api.getiter(f"/orgs/{org}/repos"):
            slug = repo["full_name"]

            _LOGGER.debug("working on %s", slug)
            if repo["archived"] or (slug == "thoth-station/notebooks"):
                _LOGGER.debug("skipping %s, this repository was archived!", slug)
                continue

            for milestone in DEFAULT_MILESTONES_THOTH:
                _LOGGER.debug("checking for %s", milestone)

                await create_or_update_milestone(
                    slug, milestone["title"], milestone["description"], due_on=milestone["due_on"],
                )


if __name__ == "__main__":
    _LOGGER.info(f"updating milestones")
    asyncio.run(update_milestones(org="thoth-station"))
