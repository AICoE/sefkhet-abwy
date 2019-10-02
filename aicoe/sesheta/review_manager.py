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


import asyncio
import pathlib
import logging

from datetime import datetime

from octomachinery.app.server.runner import run as run_app
from octomachinery.app.routing import process_event_actions
from octomachinery.app.routing.decorators import process_webhook_payload
from octomachinery.app.runtime.context import RUNTIME_CONTEXT

from thoth.common import init_logging


__version__ = "0.1.0"


init_logging()

_LOGGER = logging.getLogger(__name__)
_LOGGER.info(f"AICoE's Review Manager, Version v{__version__}")


@process_event_actions("pull_request", {"opened", "edited"})
@process_webhook_payload
async def on_pr_check_wip(*, action, number, pull_request, repository, sender, organization, installation, changes):
    """React to an opened or changed PR event.

    Send a status update to GitHub via Checks API.
    """
    github_api = RUNTIME_CONTEXT.app_installation_client

    check_run_name = "Sesheta work-in-progress state"

    pr_head_branch = pull_request["head"]["ref"]
    pr_head_sha = pull_request["head"]["sha"]
    repo_url = pull_request["head"]["repo"]["url"]
    issue_url = pull_request["issue_url"]

    check_runs_base_uri = f"{repo_url}/check-runs"

    issue_labels_response = await github_api.getitem(f"{issue_url}/labels", preview_api_version="symmetra")

    resp = await github_api.post(
        check_runs_base_uri,
        preview_api_version="antiope",
        data={
            "name": check_run_name,
            "head_branch": pr_head_branch,
            "head_sha": pr_head_sha,
            "status": "queued",
            "started_at": f"{datetime.utcnow().isoformat()}Z",
        },
    )

    check_runs_updates_uri = f'{check_runs_base_uri}/{resp["id"]:d}'

    resp = await github_api.patch(
        check_runs_updates_uri, preview_api_version="antiope", data={"name": check_run_name, "status": "in_progress"}
    )

    pr_title = pull_request["title"].lower()
    wip_markers = ("wip", "🚧", "dnm", "work in progress", "work-in-progress", "do not merge", "do-not-merge", "draft")

    is_wip_pr = any(m in pr_title for m in wip_markers)

    if is_wip_pr:
        try:
            await github_api.post(
                f"{issue_url}/labels",
                preview_api_version="symmetra",
                data={"labels": ["do-not-merge/work-in-progress"]},
            )
        except gidgethub.BadRequest as err:
            if err.status_code != 202:
                _LOGGER.error(err)
    else:
        try:
            await github_api.delete(
                f"{issue_url}/labels/do-not-merge%2Fwork-in-progress", preview_api_version="symmetra"
            )
        except gidgethub.BadRequest as err:
            if err.status_code != 200:
                _LOGGER.error(err)

    await github_api.patch(
        check_runs_updates_uri,
        preview_api_version="antiope",
        data={
            "name": check_run_name,
            "status": "completed",
            "conclusion": "success" if not is_wip_pr else "neutral",
            "completed_at": f"{datetime.utcnow().isoformat()}Z",
            "output": {
                "title": "🤖 This PR is NOT work-in-progress: Good to go",
                "text": "Debug info:\n"
                f"is_wip_pr={is_wip_pr!s}\n"
                f"pr_title={pr_title!s}\n"
                f"wip_markers={wip_markers!r}",
                "summary": "This change is no longer work-in-progress.",
            }
            if not is_wip_pr
            else {
                "title": "🤖 This PR is work-in-progress: " "It is incomplete",
                "text": "Debug info:\n"
                f"is_wip_pr={is_wip_pr!s}\n"
                f"pr_title={pr_title!s}\n"
                f"wip_markers={wip_markers!r}",
                "summary": "🚧 Please do not merge this PR as it is still work-in-progress.",
            },
        },
    )


if __name__ == "__main__":
    _LOGGER.setLevel(logging.DEBUG)
    _LOGGER.debug("Debug mode turned on")

    run_app(name="review-manager", version=__version__, url="https://github.com/apps/review-manager")
