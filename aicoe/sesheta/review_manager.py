#!/usr/bin/env python3
# Sefkhet-Abwy
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

from prometheus_async.aio import time

from expiringdict import ExpiringDict

from aicoe.sesheta.actions.pull_request import (
    merge_master_into_pullrequest2,
    handle_release_pull_request,
)
from aicoe.sesheta.actions import (
    do_not_merge,
    local_check_gate_passed,
    conclude_reviewer_list,
    unpack,
    needs_rebase_label,
    needs_approved_label,
    needs_size_label,
)
from aicoe.sesheta.utils import notify_channel, hangouts_userid, realname, random_positive_emoji2
from thoth.common import init_logging


import aicoe.sesheta.metrics as metrics


__version__ = "0.11.0"


init_logging(logging_env_var_start="SEFKHET__ABWY_LOG_")

_LOGGER = logging.getLogger("aicoe.sesheta")
_LOGGER.info(f"AICoE's SrcOps Cyborg, Version v{__version__}")
logging.getLogger("octomachinery").setLevel(logging.DEBUG)
logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)

notifications = ExpiringDict(max_len=100, max_age_seconds=10)


def send_notification(repository_name: str, pull_request_id: int, requested_reviewer_login: str) -> bool:
    """Decide if we need to send a notification."""
    if requested_reviewer_login == "sesheta":
        return False  # we never want to send notifications for Sesheta

    if notifications.get(f"{repository_name}_{pull_request_id}_{requested_reviewer_login}"):
        return False

    notifications[f"{repository_name}_{pull_request_id}_{requested_reviewer_login}"] = True

    return True


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


@process_event_actions("pull_request", {"closed"})
@process_webhook_payload
@time(metrics.REQ_TIME)
async def on_pr_closed(*, action, number, pull_request, repository, sender, organization, installation, **kwargs):
    """React to an closed PR event."""
    _LOGGER.debug(f"on_pr_closed: working on PR {pull_request['html_url']}")

    # we do not notify on standard automated SrcOps
    ignore_messages = ["Automatic update of dependency", "Release of", "Automatic dependency re-locking"]
    if not pull_request["title"].startswith(tuple(ignore_messages)):
        if pull_request["merged"]:
            notify_channel(
                "plain",
                f"👌 Pull Request *{pull_request['title']}* has been merged by '{realname(sender['login'])}' 🍻",
                f"pull_request_{repository['name']}_{pull_request['id']}",
                pull_request["html_url"],
            )

        else:
            notify_channel(
                "plain",
                f"👌 Pull Request *{pull_request['title']}* has been *closed* with *unmerged commits*! 🚧",
                f"pull_request_{repository['name']}_{pull_request['id']}",
                pull_request["html_url"],
            )
    elif pull_request["title"].startswith("Release of"):
        commit_hash, release = await handle_release_pull_request(pull_request)

        notify_channel(
            "plain",
            f" I have tagged {commit_hash} to be release {release} of"
            f" {pull_request['base']['repo']['full_name']} " + random_positive_emoji2(),
            f"pull_request_{repository['name']}",
            pull_request["url"],
        )


@process_event_actions("pull_request", {"opened", "reopened", "synchronize", "edited"})
@process_webhook_payload
async def on_pr_open_or_edit(*, action, number, pull_request, repository, sender, organization, installation, **kwargs):
    """React to an opened or changed PR event.

    Send a status update to GitHub via Checks API.
    """
    _LOGGER.debug(f"on_pr_open_or_edit: working on PR {pull_request['html_url']}")

    github_api = RUNTIME_CONTEXT.app_installation_client

    if action in ["opened", "reopened"]:
        # we do not notify on standard automated SrcOps
        if not pull_request["title"].startswith("Automatic ") and not pull_request["title"].startswith("Release of"):
            notify_channel(
                "plain",
                f"🆕 {pull_request['html_url']} a new Pull Request has been *opened*!",
                f"pull_request_{repository['name']}_{pull_request['id']}",
                pull_request["html_url"],
            )

        if pull_request["title"].startswith("Automatic update of dependency"):
            _LOGGER.debug(f"on_pr_open_or_edit: automatic update, will auto-approve {pull_request['html_url']}!")

            try:
                await github_api.post(
                    f"{pull_request['issue_url']}/labels", preview_api_version="symmetra", data={"labels": ["approved"]},
                )
            except gidgethub.BadRequest as err:
                if err.status_code != 202:
                    _LOGGER.error(str(err))

    try:
        await merge_master_into_pullrequest2(
            pull_request["base"]["user"]["login"], pull_request["base"]["repo"]["name"], pull_request["id"],
        )
    except gidgethub.BadRequest as err:
        _LOGGER.warning(
            f"merge_master_into_pullrequest2: status_code={err.status_code}, {str(err)}, {pull_request['html_url']}",
        )


@process_event_actions("pull_request_review", {"submitted"})
@process_webhook_payload
async def on_pull_request_review(*, action, review, pull_request, **kwargs):
    """React to Pull Request Review event."""
    _LOGGER.debug(f"on_pull_request_review: working on PR {pull_request['html_url']}")

    notification_text = ""
    needs_rebase = await needs_rebase_label(pull_request)

    if needs_rebase:
        await merge_master_into_pullrequest2(
            pull_request["base"]["user"]["login"], pull_request["base"]["repo"]["name"], pull_request["id"],
        )

    if review["state"] == "approved":
        notification_text = f"📗 '{realname(review['user']['login'])}' *approved* this Pull Request!"
        await needs_approved_label(pull_request)
    else:
        notification_text = f"📔 some new comment by '{realname(review['user']['login'])}' has arrived..."

    notify_channel(
        "plain",
        notification_text,
        f"pull_request_{kwargs['repository']['name']}_{pull_request['id']}",
        pull_request["html_url"],
    )


@process_event_actions("pull_request", {"review_requested"})
@process_webhook_payload
async def on_pull_request_review_requested(*, action, number, pull_request, requested_reviewer, **kwargs):
    """Someone requested a Pull Request Review, so we notify the Google Hangouts Chat Room."""
    _LOGGER.debug(
        f"on_pull_request_review_requested: working on PR '{pull_request['title']}' {pull_request['html_url']}",
    )

    # we do not notify on standard automated SrcOps
    if pull_request["title"].startswith("Automatic update of dependency") or pull_request["title"].startswith(
        "Release of",
    ):
        return

    for requested_reviewer in pull_request["requested_reviewers"]:
        if send_notification(kwargs["repository"]["name"], pull_request["id"], requested_reviewer["login"]):
            _LOGGER.info(f"requesting review by {requested_reviewer['login']} on {pull_request['html_url']}")

            notify_channel(
                "plain",
                f"🔎 a review by " f"{hangouts_userid(requested_reviewer['login'])}" f" has been requested",
                f"pull_request_{kwargs['repository']['name']}_{pull_request['id']}",
                pull_request["html_url"],
            )


@process_event_actions("issues", {"opened", "reopened"})
@process_webhook_payload
async def on_issue_opened(*, action, issue, repository, sender, **kwargs):
    """Take actions if an issue got opened."""
    _LOGGER.info(f"working on Issue {issue['html_url']}: opened")

    if issue["title"].startswith("Automatic update of dependency"):
        _LOGGER.debug(f"{issue['url']} is an 'Automatic update of dependencies', not sending notification")
        return

    if issue["title"].startswith("Automatic dependency re-locking"):
        _LOGGER.debug(f"{issue['url']} is an 'Automatic dependency re-locking', not sending notification")
        return

    if issue["title"].startswith("Initial dependency lock"):
        _LOGGER.debug(f"{issue['url']} is an 'Initial dependency lock', not sending notification")
        return

    if issue["title"].startswith("Failed to update dependencies"):
        _LOGGER.debug(f"{issue['url']} is an 'Failed to update dependencies', not sending notification")
        return

    if issue["title"].startswith("Release of version"):
        _LOGGER.debug(f"{issue['url']} is a 'release issue'")

        github_api = RUNTIME_CONTEXT.app_installation_client

        await github_api.post(
            f"{issue['url']}/labels", preview_api_version="symmetra", data={"labels": ["bot"]},
        )

    notify_channel(
        "plain",
        f"{realname(issue['user']['login'])} just opened an issue: *{issue['title']}*... 🚨 "
        f"check {issue['html_url']} for details",
        f"issue_{repository['name']}_{issue['id']}",
        issue["html_url"],
    )


@process_event_actions("issues", {"labeled"})
@process_webhook_payload
async def on_issue_labeled(*, action, issue, label, repository, organization, sender, installation):
    """Take actions if an issue got labeled.

    If it is labeled 'bug' we add the 'human_intervention_required' label
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


@process_event_actions("issue_comment", {"created"})
@process_webhook_payload
async def on_check_gate(*, action, issue, comment, repository, organization, sender, installation):
    """Determine if a 'check' gate was passed and the Pull Request is ready for review.

    If the Pull Request is ready for review, assign a set of reviewers.
    """
    _LOGGER.debug(f"looking for a passed 'check' gate: {issue['url']}")

    if comment["body"].startswith("Build succeeded."):
        _LOGGER.debug(f"local/check status might have changed...")

        pr_url = issue["url"].replace("issues", "pulls")
        pr_body_ok = False

        github_api = RUNTIME_CONTEXT.app_installation_client
        pr = await github_api.getitem(pr_url)
        do_not_merge_label = await do_not_merge(pr_url)
        gate_passed = await local_check_gate_passed(pr_url)
        reviewer_list = await conclude_reviewer_list(pr["base"]["repo"]["owner"]["login"], pr["base"]["repo"]["name"])
        current_reviewers = pr["requested_reviewers"]
        pr_owner = pr["user"]["login"]

        # TODO check if PR body is ok

        # TODO check for size label

        _LOGGER.debug(f"gate passed: {gate_passed}, do_not_merge_label: {do_not_merge_label}, body_ok: {pr_body_ok}")

        if gate_passed and not do_not_merge_label:
            _LOGGER.debug(f"PR {pr['html_url']} is ready for review!")

            # we do not notify on standard automated SrcOps
            if not pr["title"].startswith("Automatic update of dependency") and not pr["title"].startswith(
                "Release of",
            ):
                notify_channel(
                    "plain",
                    f"🎉 This Pull Request seems to be *ready for review*... the local/check gate has been passed! 💚",
                    f"pull_request_{repository['name']}_{pr['id']}",
                    "thoth-station",
                )

            if reviewer_list is not None:
                _LOGGER.debug(f"PR {pr['html_url']} could be reviewed by {unpack(reviewer_list)}")

        elif not gate_passed and not len(current_reviewers) == 0:
            # if a review has been started we should not remove the reviewers
            _LOGGER.debug(
                f"PR {pr['html_url']} is NOT ready for review! Removing reviewers: {unpack(current_reviewers)}",
            )


async def on_security_advisory(*, action, security_advisory, **kwargs):
    """Send a notification to Hangout."""
    _LOGGER.warning(
        f"New information wrt GitHub security advisory {security_advisory['ghsa_id']} '{security_advisory['summary']}'",
    )

    ecosystem_name = security_advisory["vulnerabilities"]["package"]["ecosystem"]
    references_url = security_advisory["references"]["url"]

    notify_channel(
        "plain",
        f"🙀 🔐 GitHub issued some information on security advisory {security_advisory['ghsa_id']}, "
        f"it is related to {ecosystem_name} ecosystem: "
        f"{security_advisory['description']}"
        f" see also: {references_url}",
        f"{security_advisory['ghsa_id']}",
        "thoth-station",
    )


if __name__ == "__main__":
    _LOGGER.setLevel(logging.DEBUG)
    _LOGGER.debug("Debug mode turned on")

    run_app(  # pylint: disable=expression-not-assigned
        name="Sefkhet-Abwy",
        version=get_version_from_scm_tag(root="../..", relative_to=__file__),
        url="https://github.com/apps/Sefkhet-Abwy",
    )
