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

from datetime import datetime

import gidgethub

from octomachinery.github.api.tokens import GitHubOAuthToken
from octomachinery.github.api.raw_client import RawGitHubAPI
from octomachinery.app.runtime.context import RUNTIME_CONTEXT

from aicoe.sesheta.actions.common import get_master_head_sha, get_pull_request, trigger_update_branch

from thoth.common import init_logging


init_logging()

_LOGGER = logging.getLogger(__name__)


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


async def merge_master_into_pullrequest2(owner: str, repo: str, pull_request: int):
    """Merge the master branch into the Pull Request."""
    github_api = RUNTIME_CONTEXT.app_installation_client
    head_sha = await get_master_head_sha(owner, repo)
    _r = await get_pull_request(owner, repo, pull_request)

    rebaseable = _r["rebaseable"]
    base_sha = _r["base"]["sha"]

    _LOGGER.debug(f"head: {head_sha}, base: {base_sha}, rebaseable: {rebaseable}")

    # TODO if rebaseable is None, we need to come back in a few seconds, github has not finished a background task
    if rebaseable and (base_sha != head_sha):
        _LOGGER.debug(
            f"rebasing Pull Request {pull_request} in {owner}/{repo} into master"
            f", head sha = {head_sha} and pull requests's base sha = {base_sha}"
        )

        await github_api.put(
            f"/repos/{owner}/{repo}/pulls/{pull_request}/update-branch", preview_api_version="lydian", data=b""
        )
    else:
        _LOGGER.debug(f"not triggering a rebase, head sha = {head_sha} and pull requests's base sha = {base_sha}")


async def needs_approved_label(_pull_request: dict = None) -> bool:
    """Add a 'approved' label if review approved."""
    github_api = RUNTIME_CONTEXT.app_installation_client
    issue_url = _pull_request["issue_url"]
    pull_request = await github_api.getitem(_pull_request["url"])

    _LOGGER.debug(f"checking if {pull_request['html_url']} needs a approved label")

    needs_approved_actual = await is_mergeable(pull_request)
    has_approved_label = has_label(pull_request, "approved")

    if needs_approved_actual and not has_approved_label:
        _LOGGER.debug(f"adding 'approved' label to {pull_request['html_url']}")

        try:
            await github_api.post(f"{issue_url}/labels", preview_api_version="symmetra", data={"labels": ["approved"]})
            return True
        except gidgethub.BadRequest as err:
            if err.status_code != 202:
                _LOGGER.error(str(err))
    else:

        return False


async def needs_rebase_label(_pull_request: dict = None) -> bool:
    """Add a 'needs-rebase' labels if required."""
    github_api = RUNTIME_CONTEXT.app_installation_client
    issue_url = _pull_request["issue_url"]
    pull_request = await github_api.getitem(_pull_request["url"])

    _LOGGER.debug(f"checking if {pull_request['html_url']} needs a rebase label")

    needs_rebase_actual = await is_mergeable(pull_request)
    has_rebase_label = has_label(pull_request, "do-not-merge/needs-rebase")

    if needs_rebase_actual and not has_rebase_label:
        _LOGGER.debug(f"adding 'needs-rebase' label to {pull_request['html_url']}")

        try:
            await github_api.post(
                f"{issue_url}/labels", preview_api_version="symmetra", data={"labels": ["do-not-merge/needs-rebase"]}
            )
            return True
        except gidgethub.BadRequest as err:
            if err.status_code != 202:
                _LOGGER.error(str(err))

    elif not needs_rebase_actual and has_rebase_label:
        _LOGGER.debug(f"removing 'needs-rebase' label from {pull_request['html_url']}")

        try:
            await github_api.delete(f"{issue_url}/labels/do-not-merge%2Fneeds-rebase", preview_api_version="symmetra")
        except gidgethub.BadRequest as err:
            _LOGGER.info(str(err))

        return False

    else:

        return False


async def manage_label_and_check(github_api=None, pull_request: dict = None):
    """Mange the WIP label and check for this Pull Request."""
    check_runs_updates_uri = None

    if pull_request is None:
        return

    if github_api is None:
        _LOGGER.error("no GitHub API object provided... bailing out!")
        return

    check_run_name = "Sesheta work-in-progress state"

    pr_head_sha = pull_request["merge_commit_sha"]
    if pr_head_sha is None:
        pr_head_sha = pull_request["head"]["sha"]

    repo_url = pull_request["base"]["repo"]["url"]
    issue_url = pull_request["issue_url"]

    check_runs_base_uri = f"{repo_url}/check-runs"

    _LOGGER.debug(f"manage_label_and_check: check_runs base uri: {check_runs_base_uri}, PR head sha: {pr_head_sha}")

    issue_labels_response = await github_api.getitem(f"{issue_url}/labels", preview_api_version="symmetra")

    try:
        resp = await github_api.post(
            check_runs_base_uri,
            preview_api_version="antiope",
            data={
                "name": check_run_name,
                "head_sha": pr_head_sha,
                "status": "queued",
                "started_at": f"{datetime.utcnow().isoformat()}Z",
            },
        )

        check_runs_updates_uri = f'{check_runs_base_uri}/{resp["id"]:d}'
    except gidgethub.BadRequest as err:
        _LOGGER.error(f"status_code={err.status_code}, {str(err)}")

    if check_runs_updates_uri is not None:
        try:
            resp = await github_api.patch(
                check_runs_updates_uri,
                preview_api_version="antiope",
                data={"name": check_run_name, "status": "in_progress"},
            )
        except gidgethub.BadRequest as err:
            _LOGGER.error(f"status_code={err.status_code}, {str(err)}")

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
            if err.status_code == 404:  # This is ok, label was not present......
                pass
            elif err.status_code != 200:
                _LOGGER.error(err)

    if check_runs_updates_uri is not None:
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
                    "title": "🤖 This PR is work-in-progress: It is incomplete",
                    "text": "Debug info:\n"
                    f"is_wip_pr={is_wip_pr!s}\n"
                    f"pr_title={pr_title!s}\n"
                    f"wip_markers={wip_markers!r}",
                    "summary": "🚧 Please do not merge this PR as it is still work-in-progress.",
                },
            },
        )


async def local_check_gate_passed(pr_url: str) -> bool:
    """Check if the Pull Request has passed the 'local/check' gate successfully."""
    gate_pass_status = None

    try:
        github_api = RUNTIME_CONTEXT.app_installation_client

        pr = await github_api.getitem(pr_url)

        async for commit in github_api.getiter(f"{pr_url}/commits"):
            # let's get the HEAD ref of the PR
            if commit["sha"] == pr["head"]["sha"]:
                statuses = await github_api.getitem(f"{commit['url']}/statuses")

                # according to https://developer.github.com/v3/repos/statuses/#list-statuses-for-a-specific-ref
                # the first of list is the latest status
                gate_pass_status = statuses[0]  # FIXME except KeyError
    except Exception as err:
        _LOGGER.error(str(err))

    if gate_pass_status is not None:
        if (gate_pass_status["context"] == "local/check") and (gate_pass_status["state"] == "success"):
            return True

    return False


async def is_mergeable(pull_request: dict = None) -> bool:
    """Determine if the Pull Request is mergeable."""
    if pull_request["merged"]:
        return False

    if not pull_request["mergeable"]:
        return True

    return False


def has_label(pull_request: dict, label: str) -> bool:
    """Check if 'label' is present for the given Pull Request."""
    if pull_request["labels"] == []:
        return False

    for github_label in pull_request["labels"]:
        if label in github_label["name"]:
            return True

    return False


if __name__ == "__main__":
    pass
