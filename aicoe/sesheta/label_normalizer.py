#!/usr/bin/env python3
# Sesheta
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


"""This will normalize some standard labels."""


import os
import asyncio
import logging

from datetime import datetime

from octomachinery.github.api.tokens import GitHubOAuthToken
from octomachinery.github.api.raw_client import RawGitHubAPI

from thoth.common import init_logging
from aicoe.sesheta.actions import __version__
from aicoe.sesheta.actions.label import DEFAULT_LABELS, create_or_update_label


REPOS = ["AICoE/sesheta", "thoth-station/srcops-testing"]


init_logging()

_LOGGER = logging.getLogger(__name__)
_LOGGER.info(f"Sesheta action: label_normalizer, Version v{__version__}")


async def update_labels(org: str):
    """Update Labels to comply to our standard."""
    access_token = GitHubOAuthToken(os.environ["GITHUB_ACCESS_TOKEN"])
    github_api = RawGitHubAPI(access_token, user_agent="sesheta-actions")

    repos = await github_api.getitem(f"/orgs/{org}/repos")

    for repo in repos:
        slug = f"{org}/{repo['name']}"
        for label in DEFAULT_LABELS:
            _LOGGER.debug(f"looking for {label['name']} in {slug}")
            await create_or_update_label(slug, label["name"], label["color"])


if __name__ == "__main__":
    for org in ["AICoE", "thoth-station"]:
        asyncio.run(update_labels(org))
