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
    {"name": "approved", "color": "00cc00", "description": ""},
    {"name": "do-not-merge", "color": "cc0000", "description": ""},
    {"name": "do-not-merge/work-in-progress", "color": "cc0000", "description": ""},
    {"name": "do-not-merge/hold", "color": "cc0000", "description": ""},
    {"name": "do-not-merge/invalid-owners-file", "color": "cc0000", "description": ""},
    {"name": NEEDS_REBASE_LABEL_NAME, "color": "cc0000", "description": "The head of the PR needs to be rebased."},
    {"name": "work-in-progress", "color": "cc0000", "description": "... we are working on it!"},
    {"name": "needs-rebase", "color": "cc0000", "description": "The head of the PR needs to be rebased."},
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
    {
        "name": "priority/critical-urgent",
        "color": "e11d21",
        "description": "A critical item needing immediate treatments!",
    },
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
    {"name": "kind/feature", "color": "a5d5f7", "description": "Categorize Issue or PR as related to a new feature."},
    {"name": "kind/bug", "color": "d73a4a", "description": "Categorize Issue or PR as related to a bug."},
    {"name": "kind/question", "color": "d73a4a", "description": "Categorize Issue as a User question."},
    {"name": "kind/flake", "color": "f3ccff", "description": "A test flake."},
    {
        "name": "priority/critical-urgent",
        "color": "ff0000",
        "description": "Highest priority. Must be actively worked on as someone's top priority right now.",
    },
    {
        "name": "priority/important-longterm",
        "color": "ff9900",
        "description": "Important over the long term, but may not be staffed and/or may need multiple releases to complete.",
    },
    {
        "name": "priority/important-soon",
        "color": "ffcd00",
        "description": "Must be staffed and worked on either currently, or very soon, ideally in time for the next release.",
    },
    {
        "name": "deployment_name/moc",
        "color": "d5f48d",
        "description": "This issue is related to our deployment on MOC",
    },
    {
        "name": "deployment_name/ocp-test",
        "color": "d5f48d",
        "description": "this issue is related to our test environment deployment on ocp/psi",
    },
    {
        "name": "deployment_name/ocp-stage",
        "color": "d5f48d",
        "description": "this issue is related to our stage environment deployment on ocp/psi",
    },
    {
        "name": "hacktoberfest-accepted",
        "color": "d4c5f9",
        "description": "This Pull Request has been accepted for Hacktoberfest 2020!",
    },
    {
        "name": "sig/documentation",
        "color": "1d76db",
        "description": "Issues or PRs related to documentation, tutorials, examples, ...",
    },
    {
        "name": "sig/cyborgs",
        "color": "1d76db",
        "description": "Issues or PRs related to Kebechet and all the other Cyborgs.",
    },
    {
        "name": "sig/investigator",
        "color": "1d76db",
        "description": "Issues or PRs related to https://github.com/orgs/thoth-station/projects/14",
    },
    {
        "name": "sig/indicators",
        "color": "1d76db",
        "description": "Issues or PRs related to {meta|performance|security} indicators.",
    },
    {
        "name": "sig/knowledge-graph",
        "color": "1d76db",
        "description": "Issues or PRs related to https://github.com/orgs/thoth-station/projects/8",
    },
    {"name": "sig/solvers", "color": "1d76db", "description": "Issues or PRs related to Solvers"},
    {
        "name": "sig/slo",
        "color": "1d76db",
        "description": "Issues or PRs related to Service Level Indicators and Objectives and their reporting",
    },
    {
        "name": "sig/advisor",
        "color": "1d76db",
        "description": "Issues or PRs related to https://github.com/orgs/thoth-station/projects/4",
    },
    {
        "name": "sig/build",
        "color": "1d76db",
        "description": "Issues or PRs related to building and continuous delivery of build artifacts.",
    },
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
                    f"/repos/{slug}/labels", preview_api_version="symmetra", data={"name": name, "color": color},
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
