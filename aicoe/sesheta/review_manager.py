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

from datetime import datetime

import gidgethub

from octomachinery.app.server.runner import run as run_app
from octomachinery.app.routing import process_event_actions
from octomachinery.app.routing.decorators import process_webhook_payload
from octomachinery.app.runtime.context import RUNTIME_CONTEXT
from octomachinery.github.api.tokens import GitHubOAuthToken
from octomachinery.github.api.raw_client import RawGitHubAPI

from aicoe.sesheta.actions.pull_request import manage_label_and_check, merge_master_into_pullrequest
from thoth.common import init_logging


__version__ = "0.1.0-dev"


init_logging()

_LOGGER = logging.getLogger(__name__)
_LOGGER.info(f"AICoE's Review Manager, Version v{__version__}")


@process_event_actions("pull_request", {"opened", "edited"})
@process_webhook_payload
async def on_pr_check_wip(*, action, number, pull_request, repository, sender, organization, installation, changes):
    """React to an opened or changed PR event.

    Send a status update to GitHub via Checks API.
    """
    access_token = GitHubOAuthToken(os.environ["GITHUB_ACCESS_TOKEN"])
    github_api = RawGitHubAPI(access_token, user_agent="sesheta")
    # github_api = RUNTIME_CONTEXT.app_installation_client

    manage_label_and_check(github_api, pull_request)

    triggered = await merge_master_into_pullrequest(
        pull_request["head"]["user"]["login"],
        pull_request["head"]["repo"]["name"],
        pull_request["id"],
        token=github_api.token,
    )


if __name__ == "__main__":
    _LOGGER.setLevel(logging.DEBUG)
    _LOGGER.debug("Debug mode turned on")

    run_app(name="review-manager", version=__version__, url="https://github.com/apps/review-manager")
