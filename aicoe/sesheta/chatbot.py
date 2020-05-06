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


"""This is a Google Hangouts Chat Bot."""


import os
import asyncio
import pathlib
import logging

import aiohttp
from aiohttp import web

from thoth.common import init_logging

from aicoe.sesheta.utils import notify_channel, hangouts_userid, realname
from aicoe.sesheta.actions import __version__


init_logging(logging_env_var_start="SEFKHET__ABWY_LOG_")

_LOGGER = logging.getLogger("aicoe.sesheta")
_LOGGER.info(f"AICoE's Chat Bot, Version v{__version__}")
logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)


routes = web.RouteTableDef()
app = web.Application()


async def get_intent(text: str,) -> (str, float, dict):
    """Get the Intent of the provided text, and assign it a score."""
    repo_name = None
    tag = None

    if text.startswith("assign"):
        return ("assign", 1.0, {})

    if text.startswith("get tags of"):
        repo_name = text.split(" ")[-1]

        return ("get_tags_of_repo", 1.0, {"repo_name": repo_name})

    if text.startswith("deliver"):
        repo_name_tag = text.split(" ")[-1]

        try:
            (repo_name, tag) = repo_name_tag.split(":")
        except Exception as e:
            pass

        return ("tag_release", 1.0, {"repo_name": repo_name, "tag": tag})

    return (None, 0.0, {})


async def process_user_text(thread_id: str, text: str) -> str:
    """Process the Text, get the intent, and schedule actions accordingly."""
    _LOGGER.info(f"message on thread {thread_id}: {text}")

    intent = await get_intent(text)

    if intent[0] == "get_tags_of_repo":
        _LOGGER.info(f"get tags of repo... {intent}")

    if intent[0] == "tag_release":
        _LOGGER.info(f"tag_release... {intent}")

        if (intent[2]['tag'] is None) or (intent[2]['repo_name'] is None):
            return "Uhh... cant find repo_name or tag, please use `repo_name:tag`!"

        webhook_payload = {
            "ref": intent[2]["tag"],
            "ref_type": "tag",
            "repo_url": f"https://github.com/thoth-station/{intent[2]['repo_name']}",
            "repo_name": intent[2]["repo_name"],
        }
        webhook_url = "http://thoth-ci.thoth.ultrahook.com"

        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=webhook_payload) as resp:
                _LOGGER.debug(resp.status)
                _LOGGER.debug(await resp.text())

        return f"I have told TektonCD to deliver `{intent[2]['tag']}` of repository `{intent[2]['repo_name']}`, let's see what happens..."

    return "Sorry, I didnt get that... try 'deliver' or 'get tags of'"


@routes.get("/")
async def hello(request):
    """Print just a Hello World."""
    return web.Response(text="Hello, world")


@routes.post("/api/v1alpha1")
async def hangouts_handler(request):
    """Handle Google Hangouts Chat incoming webhooks."""
    event = await request.json()

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
