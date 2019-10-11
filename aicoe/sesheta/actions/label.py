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

import os
import logging

import gidgethub

from octomachinery.github.api.tokens import GitHubOAuthToken
from octomachinery.github.api.raw_client import RawGitHubAPI
from octomachinery.app.runtime.context import RUNTIME_CONTEXT

from thoth.common import init_logging


init_logging()

_LOGGER = logging.getLogger(__name__)


DEFAULT_LABELS = [
    {"name": "bot", "color": "698b69"},
    {"name": "approved", "color": "00cc00"},
    {"name": "do-not-merge", "color": "cc0000"},
    {"name": "do-not-merge/work-in-progress", "color": "cc0000"},
    {"name": "do-not-merge/needs-rebase", "color": "cc0000"},
    {"name": "work-in-progress", "color": "cc0000"},
    {"name": "needs-rebase", "color": "cc0000"},
    {"name": "human_intervention_required", "color": "f3ccff"},
    {"name": "potential_flake", "color": "f3ccff"},
    {"name": "test:flake", "color": "f3ccff"},
    {"name": "priority/critical-urgent", "color": "e11d21"},
    {"name": "hacktoberfest", "color": "99cdf8", "description": "This might be something for Hacktoberfest"},
    {
        "name": "size/XS",
        "color": "00ff00",
        "description": "Denotes a PR that changes 0-9 lines, ignoring generated files.",
    },
    {
        "name": "size/S",
        "color": "00aa00",
        "description": "Denotes a PR that changes 10-29 lines, ignoring generated files.",
    },
    {
        "name": "size/M",
        "color": "999900",
        "description": "Denotes a PR that changes 30-99 lines, ignoring generated files.",
    },
    {
        "name": "size/L",
        "color": "ffff00",
        "description": "Denotes a PR that changes 100-299 lines, ignoring generated files.",
    },
    {
        "name": "size/XL",
        "color": "ff9900",
        "description": "Denotes a PR that changes 300-499 lines, ignoring generated files.",
    },
    {
        "name": "size/XXL",
        "color": "ff0000",
        "description": "Denotes a PR that changes 500++ lines, ignoring generated files.",
    },
]


async def create_or_update_label(slug: str, name: str, color: str = "") -> str:
    """Create or update the label in the given repository."""
    access_token = GitHubOAuthToken(os.environ["GITHUB_ACCESS_TOKEN"])
    github_api = RawGitHubAPI(access_token, user_agent="sesheta-actions")

    try:
        label = await github_api.getitem(f"/repos/{slug}/labels/{name}", preview_api_version="symmetra")

        if label["color"] != color:
            await github_api.patch(
                f"/repos/{slug}/labels/{name}", preview_api_version="symmetra", data={"new_name": name, "color": color}
            )

    except gidgethub.BadRequest as bad:
        _LOGGER.error(f"Label '{name}', Repo: '{slug}': {bad}")

        try:
            resp = await github_api.post(
                f"/repos/{slug}/labels", preview_api_version="symmetra", data={"name": name, "color": color}
            )
        except gidgethub.BadRequest as created:
            _LOGGER.info(f"Label '{name}', Repo: '{slug}': created")  # TODO maybe this should be a little more robust?
    return


async def do_not_merge(pr_url: str) -> bool:
    """Check if the given Pull Request has any of the DNM labels."""
    try:
        github_api = RUNTIME_CONTEXT.app_installation_client

        pr = await github_api.getitem(pr_url)

        for label in pr["labels"]:
            if label["name"].startswith("do-not-merge") or label["name"].startswith("work-in-progress"):
                return True

    except Exception as err:
        _LOGGER.error(str(err))

    return False
