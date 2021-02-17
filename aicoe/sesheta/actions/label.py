#!/usr/bin/env python3
# sesheta-actions
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


"""Sesheta's actions."""


import os
import logging

from datetime import datetime

import aiohttp
import gidgethub

from octomachinery.github.api.tokens import GitHubOAuthToken
from octomachinery.github.api.raw_client import RawGitHubAPI
from octomachinery.app.runtime.context import RUNTIME_CONTEXT


_LOGGER = logging.getLogger(__name__)

NEEDS_REBASE_LABEL_NAME = "do-not-merge/needs-rebase"
GITHUB_DEFAULT_LABELS = [
    "bug",
    "documentation",
    "duplicate",
    "enhancement",
    "good first issue",
    "help wanted",
    "invalid",
    "question",
    "wontfix",
]

DEFAULT_LABELS = [
    {"name": "bot", "color": "698b69", "description": "to a cyborg team mate!"},
    {"name": "human_intervention_required", "color": "f3ccff", "description": "to a human team mate!"},
    {"name": "thoth/human_intervention_required", "color": "f3ccff", "description": "to a human team mate!"},
    {
        "name": "thoth/potential-observation",
        "color": "f3ccff",
        "description": "This might be an observation to be included in Thoth's Knowledge Graph",
    },
    {
        "name": "thoth/group-programming",
        "color": "3bbf72",
        "description": "A potential item for a group-programming session...",
    },
    {"name": "potential_flake", "color": "f3ccff", "description": "This might be a flake of some kind."},
    {"name": "thoth/potential-flake", "color": "f3ccff", "description": "This might be a flake of some kind."},
    {"name": "test:flake", "color": "f3ccff", "description": "A test flake."},
    {"name": "test/flake", "color": "f3ccff", "description": "A test flake."},
]

DEFAULT_MILESTONES_THOTH = [
    {"title": "v0.6.0", "description": "Tracking Milestone for v0.6.0", "due_on": "2020-05-29T19:00:00Z"},
    {"title": "v0.7.0", "description": "Security Indicator Aggregation", "due_on": "2020-06-30T23:00:00Z"},
    {"title": "v0.8.0", "description": "Advise-backed Kebechet", "due_on": "2020-07-17T23:00:00Z"},
    {"title": "adviser-v0.17.0", "description": "moar stable Adviser!", "due_on": "2020-09-14T13:00:00Z"},
    {"title": "adviser-v0.18.0", "description": "Security Indicator advise", "due_on": "2020-09-28T13:00:00Z"},
    {
        "title": "investigator-v0.5.0",
        "description": "add Kafka to our infrastructure",
        "due_on": "2020-09-28T13:00:00Z",
    },
    {"title": "slo-reporter-v0.7.0", "description": "more SLI and docs", "due_on": "2020-09-28T13:00:00Z"},
    {"title": "kebechet-v1.1.0", "description": "proactive cyborg nr. 1", "due_on": "2020-10-12T13:00:00Z"},
    {
        "title": "python38-migration",
        "description": "migrate libraries and applications to Python 3.8",
        "due_on": "2020-11-23T13:00:00Z",
    },
]


async def create_or_update_milestone(slug: str, title: str, description: str, state: str = "open", due_on: str = None):
    """Create or update the Milestone in the given repository."""
    access_token = GitHubOAuthToken(os.environ["GITHUB_ACCESS_TOKEN"])

    async with aiohttp.ClientSession() as client:
        github_api = RawGitHubAPI(access_token, session=client, user_agent="sesheta-actions")

        # prepare a milestone
        milestone_data = {"title": title, "description": description, "state": state}

        if due_on is not None:
            milestone_data["due_on"] = due_on

            due_on_datetime = datetime.strptime(due_on, "%Y-%m-%dT%H:%M:%SZ")

            if due_on_datetime < datetime.utcnow():
                _LOGGER.info(f"Milestone '{title}' has a due date in the past... skipping!")
                return

        try:
            # and see if it exists
            _LOGGER.debug("checking %s for %s", slug, title)

            async for milestone in github_api.getiter(f"/repos/{slug}/milestones"):
                _LOGGER.debug("found %s: %s", slug, milestone)

                if (milestone["title"] == title) and (
                    (milestone["due_on"] != due_on) or (milestone["description"] != description)
                ):
                    _LOGGER.debug("updating %s: %s", slug, milestone_data)
                    del milestone_data["title"]
                    await github_api.patch(f"/repos/{slug}/milestones/{milestone['number']}", data=milestone_data)

                    return

            _LOGGER.debug("creating %s: %s", slug, milestone_data)
            await github_api.post(f"/repos/{slug}/milestones", data=milestone_data)

        except gidgethub.BadRequest as bad:
            _LOGGER.error(f"Milestone '{title}', Repo: '{slug}': {bad}")

        return


async def create_or_update_label(slug: str, name: str, color: str = "") -> str:
    """Create or update the label in the given repository."""
    access_token = GitHubOAuthToken(os.environ["GITHUB_ACCESS_TOKEN"])

    async with aiohttp.ClientSession() as client:
        github_api = RawGitHubAPI(access_token, session=client, user_agent="sesheta-actions")

        try:
            _LOGGER.debug("get item...")
            label = await github_api.getitem(f"/repos/{slug}/labels/{name}", preview_api_version="symmetra")

            if label["color"] != color:
                _LOGGER.debug("patching item color...")
                await github_api.patch(
                    f"/repos/{slug}/labels/{name}",
                    preview_api_version="symmetra",
                    data={"new_name": name, "color": color},
                )

        except gidgethub.BadRequest as bad:
            _LOGGER.error(f"Label '{name}', Repo: '{slug}': {bad}")

            try:
                resp = await github_api.post(
                    f"/repos/{slug}/labels",
                    preview_api_version="symmetra",
                    data={"name": name, "color": color},
                )
            except gidgethub.BadRequest as created:
                _LOGGER.info(
                    f"Label '{name}', Repo: '{slug}': created",
                )  # TODO maybe this should be a little more robust?
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
