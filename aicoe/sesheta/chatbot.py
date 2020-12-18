#!/usr/bin/env python3
# Sefkhet-Abwy
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


"""This is a Google Hangouts Chat Bot."""


import os
import logging
import random

import aiohttp

from aiohttp import web

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

from thoth.common import init_logging

from aicoe.sesheta.messages import HELP_MESSAGE
from aicoe.sesheta.actions.chat import process_user_text
from aicoe.sesheta.utils import hangouts_userid
from aicoe.sesheta import __version__


init_logging(logging_env_var_start="SEFKHET__ABWY_LOG_")

_LOGGER = logging.getLogger("aicoe.sesheta")
_LOGGER.info(f"AICoE's Chat Bot, Version v{__version__}")
logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)
_THOTH_INHABITANTS = [
    "bissenbay",
    "fridex",
    "goern",
    "harshad16",
    "KPostOffice",
    "pacospace",
    "saisankargochhayat",
    "sub-mod",
    "xtuchyna",
]
_CHATBOT = ChatBot("Sesheta", read_only=True)
_TRAINER = ChatterBotCorpusTrainer(_CHATBOT)
_TRAINER.train("chatterbot.corpus.english")


routes = web.RouteTableDef()
app = web.Application()

GITHUB_TOKEN = os.environ["GITHUB_ACCESS_TOKEN"]


@routes.get("/")
async def hello(request):
    """Print just a Hello World."""
    return web.Response(text="Hello, world")


async def make_release_issue(request: dict):
    """Create a release issue on Github for Thoth Repos."""
    repo_name, text = request.get("repo_name"), request.get("text")
    issue_title = " ".join(text.split(" ")[1:-2])
    web_url = f"https://api.github.com/repos/thoth-station/{repo_name}/issues"
    json_payload = {"title": issue_title, "assignees": ["sesheta"], "labels": ["bot"]}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            web_url, headers={f"Authorization": f"token {GITHUB_TOKEN}"}, json=json_payload,
        ) as resp:
            status = resp.status
            resp_text = await resp.json()
            _LOGGER.debug(status, resp_text)
            if resp.status == 201:
                issue_link = resp_text.get("html_url")
                return f"Release issue is successfully created at - <{issue_link}|Link>"
    return f"Creating the issue failed. \n Log - {resp_text}"


@routes.post("/api/v1alpha1")
async def hangouts_handler(request):
    """Handle Google Hangouts Chat incoming webhooks."""
    event = await request.json()
    _LOGGER.info(f"Incoming json is - {event}")
    if event["type"] == "ADDED_TO_SPACE" and event["space"]["type"] == "ROOM":
        text = 'Thanks for adding me to "%s"!' % event["space"]["displayName"]
    elif event["type"] == "MESSAGE":
        intent = await process_user_text(event["message"]["thread"]["name"], event["message"]["text"])
        text = intent
    else:
        return
    return web.json_response({"text": text})


if __name__ == "__main__":
    _LOGGER.setLevel(logging.DEBUG)
    _LOGGER.debug("Debug mode turned on")

    app.add_routes(routes)
    web.run_app(app)
