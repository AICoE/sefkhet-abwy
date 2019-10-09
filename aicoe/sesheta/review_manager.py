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


"""This will handle all the GitHub webhooks."""


import os
import asyncio
import pathlib
import logging

import gidgethub

from octomachinery.app.server.runner import run as run_app
from octomachinery.app.routing import process_event_actions, process_event
from octomachinery.app.routing.decorators import process_webhook_payload
from octomachinery.app.runtime.context import RUNTIME_CONTEXT
from octomachinery.github.config.app import GitHubAppIntegrationConfig
from octomachinery.github.api.app_client import GitHubApp
from octomachinery.app.server.machinery import run_forever
from octomachinery.utils.versiontools import get_version_from_scm_tag


from aicoe.sesheta import get_github_client
from aicoe.sesheta.actions.pull_request import manage_label_and_check, merge_master_into_pullrequest2
from thoth.common import init_logging


__version__ = "0.2.0"


init_logging()

_LOGGER = logging.getLogger(__name__)
_LOGGER.info(f"AICoE's Review Manager, Version v{__version__}")
logging.getLogger("octomachinery").setLevel(logging.DEBUG)


@process_event("ping")
@process_webhook_payload
async def on_ping(*, hook, hook_id, zen):
    """React to ping webhook event."""
    app_id = hook["app_id"]

    _LOGGER.info("Processing ping for App ID %s " "with Hook ID %s " "sharing Zen: %s", app_id, hook_id, zen)

    _LOGGER.info("GitHub App from context in ping handler: %s", RUNTIME_CONTEXT.github_app)


@process_event("integration_installation", action="created")
@process_webhook_payload
async def on_install(
    action,  # pylint: disable=unused-argument
    installation,
    sender,  # pylint: disable=unused-argument
    repositories=None,  # pylint: disable=unused-argument
):
    """React to GitHub App integration installation webhook event."""
    _LOGGER.info("installed event install id %s", installation["id"])
    _LOGGER.info("installation=%s", RUNTIME_CONTEXT.app_installation)


@process_event_actions("pull_request", {"opened", "reopened", "synchronize", "edited"})
@process_webhook_payload
async def on_pr_open_or_edit(*, action, number, pull_request, repository, sender, organization, installation, changes):
    """React to an opened or changed PR event.

    Send a status update to GitHub via Checks API.
    """
    _LOGGER.debug(f"working on PR {pull_request['html_url']}")

    github_api = RUNTIME_CONTEXT.app_installation_client

    try:
        await manage_label_and_check(github_api, pull_request)
    except gidgethub.BadRequest as err:
        _LOGGER.error(f"status_code={err.status_code}, {str(err)}")

    try:
        await merge_master_into_pullrequest2(
            pull_request["base"]["user"]["login"], pull_request["base"]["repo"]["name"], pull_request["id"], github_api
        )
    except gidgethub.BadRequest as err:
        _LOGGER.error(f"status_code={err.status_code}, {str(err)}")


@process_event_actions("issues", {"labeled"})
@process_webhook_payload
async def on_issue_labeled(*, action, issue, label, repository, organization, sender, installation):
    """Take actions if an issue got labeled:
        if it is labeled 'bug' we add the 'human_intervention_required' label
    """
    _LOGGER.info(f"working on Issue {issue['html_url']}")
    issue_id = issue["id"]
    issue_url = issue["url"]
    issue_labels = issue["labels"]

    for label in issue_labels:
        if label["name"] == "bug":
            _LOGGER.debug(f"I found a bug!! {issue['html_url']}")

            github_api = RUNTIME_CONTEXT.app_installation_client

            try:
                await github_api.post(
                    f"{issue_url}/labels",
                    preview_api_version="symmetra",
                    data={"labels": ["human_intervention_required"]},
                )
            except gidgethub.BadRequest as err:
                if err.status_code != 202:
                    _LOGGER.error(f"status_code={err.status_code}, {str(err)}")


if __name__ == "__main__":
    _LOGGER.setLevel(logging.DEBUG)
    _LOGGER.debug("Debug mode turned on")

    run_app(  # pylint: disable=expression-not-assigned
        name="review-manager",
        version=get_version_from_scm_tag(root="../..", relative_to=__file__),
        url="https://github.com/apps/review-manager",
    )
