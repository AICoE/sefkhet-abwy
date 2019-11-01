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

"""Sesheta's actions."""


import asyncio
import os
import logging
import typing

from httplib2 import Http
from apiclient.discovery import build, build_from_document
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials

from thoth.common import init_logging


init_logging()

_LOGGER = logging.getLogger(__name__)

THOTH_DEVOPS_SPACE = os.getenv("SESHETA_GOOGLE_CHAT_SPACE", None)


def notify_channel(kind: str, message: str, thread_key: str, url: str) -> None:
    """Send message to a Google Hangouts Chat space."""
    SPACE = ""
    response = None
    scopes = ["https://www.googleapis.com/auth/chat.bot"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "/opt/app-root/etc/gcloud/sesheta-chatbot-968e13a86991.json", scopes
    )
    http_auth = credentials.authorize(Http())

    chat = build("chat", "v1", http=http_auth)

    if "thoth-station" in url:
        SPACE = THOTH_DEVOPS_SPACE
    elif "AICoE" in url:
        return
    else:
        return

    if kind.upper() in ["NEW_PULL_REQUEST", "NEW_PULL_REQUEST_REVIEW", "PULL_REQUEST_REVIEW", "REBASE_PULL_REQUEST"]:
        response = (
            chat.spaces()
            .messages()
            .create(parent=SPACE, body=create_pull_request_response(message, url), threadKey=thread_key)
        )
    elif kind.upper() == "NEW_ISSUE":
        response = (
            chat.spaces()
            .messages()
            .create(parent=SPACE, body=create_issue_response(message, url), threadKey=thread_key)
        )
    elif (kind.upper() == "MERGED_PULL_REQUEST") or (kind.upper() == "PLAIN"):
        response = chat.spaces().messages().create(parent=SPACE, body={"text": message}, threadKey=thread_key)
    elif kind.upper() == "PROMETHEUS_ALERT":
        response = (
            chat.spaces()
            .messages()
            .create(parent=SPACE, body=create_prometheus_alert(message, url), threadKey=thread_key)
        )

    if response is not None:
        response.execute()


def create_pull_request_response(message: str, url: str) -> dict:
    """Create a Google Hangouts Chat Card."""
    response = dict()
    cards = list()
    widgets = list()
    header = None

    widgets.append({"textParagraph": {"text": message}})
    widgets.append({"buttons": [{"textButton": {"text": "open this PR", "onClick": {"openLink": {"url": url}}}}]})

    cards.append({"sections": [{"widgets": widgets}]})

    response["cards"] = cards
    id = url.split("/")[-1]
    response["name"] = f"pull_request-{id}"

    return response


def create_prometheus_alert(message: str, url: str) -> dict:
    """Create a Google Hangouts Chat Card for prometheus alert."""
    response = dict()
    cards = list()
    widgets = list()

    widgets.append({"textParagraph": {"text": message}})
    widgets.append({"buttons": [{"textButton": {"text": "open the Alert", "onClick": {"openLink": {"url": url}}}}]})
    cards.append({"sections": [{"widgets": widgets}]})
    response["cards"] = cards
    response["name"] = f"prometheus_alert"
    return response


def create_issue_response(message: str, url: str) -> dict:
    """Create a Google Hangouts Chat Card."""
    response = dict()
    cards = list()
    widgets = list()
    header = None

    widgets.append({"textParagraph": {"text": message}})
    widgets.append({"buttons": [{"textButton": {"text": "open this Issue", "onClick": {"openLink": {"url": url}}}}]})
    widgets.append(
        {
            "buttons": [
                {
                    "textButton": {
                        "text": "list all open Issues",
                        "onClick": {
                            "openLink": {
                                "url": "https://github.com/issues?q=is%3Aopen+is%3Apr+archived%3Afalse+user%3Athoth-station"  # Ignore PycodestyleBear (E501)
                            }
                        },
                    }
                }
            ]
        }
    )

    cards.append({"sections": [{"widgets": widgets}]})

    response["cards"] = cards
    id = url.split("/")[-1]
    response["name"] = f"issue-{id}"

    return response
