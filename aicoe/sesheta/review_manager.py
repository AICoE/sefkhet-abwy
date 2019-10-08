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


__version__ = "0.1.0-dev"


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


@process_event_actions("pull_request", {"opened", "reopened", "synchronize", "edited"})
@process_webhook_payload
async def on_pr_open_or_edit(*, action, number, pull_request, repository, sender, organization, installation, changes):
    """React to an opened or changed PR event.

    Send a status update to GitHub via Checks API.
    """
    _LOGGER.info(f"working on PR {pull_request['html_url']}")

    github_api = RUNTIME_CONTEXT.app_installation_client

    await manage_label_and_check(github_api, pull_request)

    await merge_master_into_pullrequest2(
        pull_request["head"]["user"]["login"], pull_request["head"]["repo"]["name"], pull_request["id"], github_api
    )


if __name__ == "__main__":
    _LOGGER.setLevel(logging.DEBUG)
    _LOGGER.debug("Debug mode turned on")

    run_app(  # pylint: disable=expression-not-assigned
        name="review-manager",
        version=get_version_from_scm_tag(root="..", relative_to=__file__),
        url="https://github.com/apps/review-manager",
    )
