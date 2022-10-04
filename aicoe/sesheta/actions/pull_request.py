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


import logging

from datetime import datetime
from typing import Optional
import gidgethub

from octomachinery.github.api.tokens import GitHubOAuthToken
from octomachinery.github.api.raw_client import RawGitHubAPI
from octomachinery.app.runtime.context import RUNTIME_CONTEXT

from aicoe.sesheta.actions.common import get_master_head_sha, get_pull_request, trigger_update_branch
from aicoe.sesheta.utils import eligible_release_pullrequest, get_release_issue


_LOGGER = logging.getLogger(__name__)


async def merge_master_into_pullrequest(
    owner: str, repo: str, pull_request: int, token: str = None, dry_run: bool = False,
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
            f", head sha = {head_sha} and pull requests's base sha = {base_sha}",
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
            f", head sha = {head_sha} and pull requests's base sha = {base_sha}",
        )

        await github_api.put(
            f"/repos/{owner}/{repo}/pulls/{pull_request}/update-branch", preview_api_version="lydian", data=b"",
        )
    else:
        _LOGGER.debug(f"not triggering a rebase, head sha = {head_sha} and pull requests's base sha = {base_sha}")


async def needs_size_label(_pull_request: dict = None) -> bool:
    """Add size label to the pull request."""
    github_api = RUNTIME_CONTEXT.app_installation_client
    issue_url = _pull_request["issue_url"]
    pull_request = await github_api.getitem(_pull_request["url"])

    needs_size_actual = await is_mergeable(pull_request)
    size_label = calculate_pr_size(pull_request)
    has_size_label = get_pr_size_label(pull_request)
    _LOGGER.debug(f"calculated the size of {pull_request['html_url']} to be: {size_label}")

    if needs_size_actual and not has_size_label:
        _LOGGER.debug(f"adding '{size_label}' label to {pull_request['html_url']}")

        try:
            await github_api.post(f"{issue_url}/labels", preview_api_version="symmetra", data={"labels": [size_label]})
            return True
        except gidgethub.BadRequest as err:
            if err.status_code != 202:
                _LOGGER.error(str(err))
    elif needs_size_actual and has_size_label != size_label:
        _LOGGER.debug(f"removing pervious size label '{has_size_label}' from {pull_request['html_url']}")

        try:
            has_size_label = has_size_label.replace("/", "%2F")
            await github_api.delete(f"{issue_url}/labels/{has_size_label}", preview_api_version="symmetra")
        except gidgethub.BadRequest as err:
            _LOGGER.info(str(err))

        _LOGGER.debug(f"adding '{size_label}' label to {pull_request['html_url']}")

        try:
            await github_api.post(f"{issue_url}/labels", preview_api_version="symmetra", data={"labels": [size_label]})
            return True
        except gidgethub.BadRequest as err:
            if err.status_code != 202:
                _LOGGER.error(str(err))
    else:

        return False


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

    needs_rebase_actual = await is_rebaseable(pull_request)
    has_rebase_label = has_label(pull_request, "do-not-merge/needs-rebase")

    if needs_rebase_actual and not has_rebase_label:
        _LOGGER.debug(f"adding 'needs-rebase' label to {pull_request['html_url']}")

        try:
            await github_api.post(
                f"{issue_url}/labels", preview_api_version="symmetra", data={"labels": ["do-not-merge/needs-rebase"]},
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
                f"{issue_url}/labels/do-not-merge%2Fwork-in-progress", preview_api_version="symmetra",
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


async def is_rebaseable(pull_request: dict = None) -> bool:
    """Determine if the Pull Request is rebaseable."""
    if pull_request["merged"]:
        return False

    if not pull_request["mergeable"] and pull_request["mergeable"] is not None:
        return True

    return False


async def is_mergeable(pull_request: dict = None) -> bool:
    """Determine if the Pull Request is mergeable."""
    if pull_request["merged_at"]:
        return False
    else:
        return True


def has_label(pull_request: dict, label: str) -> bool:
    """Check if 'label' is present for the given Pull Request."""
    if pull_request["labels"] == []:
        return False

    for github_label in pull_request["labels"]:
        if label in github_label["name"]:
            return True

    return False


def get_pr_size_label(pull_request: dict) -> Optional[str]:
    """Get the pervious size label added to pull request."""
    for github_label in pull_request["labels"]:
        if "size" in github_label["name"]:
            return github_label["name"]

    return None


def calculate_pr_size(pull_request: dict) -> Optional[str]:
    """Calculate the number of additions/deletions of this Pull Request."""
    try:
        lines_changes = pull_request["additions"] + pull_request["deletions"]

        if lines_changes > 1000:
            return "size/XXL"
        elif lines_changes >= 500 and lines_changes <= 999:
            return "size/XL"
        elif lines_changes >= 100 and lines_changes <= 499:
            return "size/L"
        elif lines_changes >= 30 and lines_changes <= 99:
            return "size/M"
        elif lines_changes >= 10 and lines_changes <= 29:
            return "size/S"
        elif lines_changes >= 0 and lines_changes <= 9:
            return "size/XS"
    except KeyError as err:
        _LOGGER.error(str(err))
        return None


async def handle_release_pull_request(pullrequest: dict) -> (str, str):
    """Handle a Pull Request we created for a release."""
    github_api = RUNTIME_CONTEXT.app_installation_client

    if not eligible_release_pullrequest(pullrequest):
        _LOGGER.warning(f"Merged Release Pull Request: '{pullrequest['title']}', not eligible for release!")
        return

    commit_hash = pullrequest["merge_commit_sha"]
    release_issue = get_release_issue(pullrequest)
    release = pullrequest["head"]["ref"]

    # tag
    _LOGGER.info(f"Tagging release {release}: hash {commit_hash}.")

    tag = {"tag": str(release), "message": str(release), "object": str(commit_hash), "type": "commit"}
    response = await github_api.post(
        f"{pullrequest['base']['repo']['url']}/git/tags", preview_api_version="lydian", data=tag,
    )

    _LOGGER.debug("response: %s", response)

    tag_sha = response["sha"]

    tag_ref = {"ref": f"refs/tags/{release}", "sha": f"{tag_sha}"}
    await github_api.post(
        f"{pullrequest['base']['repo']['url']}/git/refs", data=tag_ref,
    )

    # comment on issue
    _LOGGER.info(f"Commenting on {release_issue} that we tagged {release} on hash {commit_hash}.")

    comment = {
        "body": f"I have tagged commit "
        f"[{commit_hash}]({pullrequest['base']['repo']['html_url']}/commit/{commit_hash}) "
        f"as release {release} :+1:",
    }
    await github_api.post(
        f"{pullrequest['base']['repo']['url']}/issues/{release_issue}/comments", data=comment,
    )

    # close issue
    _LOGGER.info(f"Closing {release_issue}.")

    await github_api.patch(
        f"{pullrequest['base']['repo']['url']}/issues/{release_issue}", data={"state": "closed"},
    )

    return commit_hash, release

    # happy! 💕


if __name__ == "__main__":
    pass
