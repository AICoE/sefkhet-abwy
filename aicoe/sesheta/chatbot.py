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

from aiohttp import web


from thoth.common import init_logging

from aicoe.sesheta.utils import notify_channel, hangouts_userid, realname


__version__ = "0.1.0-dev"


init_logging()

_LOGGER = logging.getLogger("aicoe.sesheta")
_LOGGER.info(f"AICoE's Chat Bot, Version v{__version__}")
logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)


routes = web.RouteTableDef()
app = web.Application()


@routes.get("/")
async def hello(request):
    return web.Response(text="Hello, world")


@routes.post("/api/v1alpha1")
async def hangouts_handler(request):
    event = await request.json()

    if event["type"] == "ADDED_TO_SPACE" and event["space"]["type"] == "ROOM":
        text = 'Thanks for adding me to "%s"!' % event["space"]["displayName"]
    elif event["type"] == "MESSAGE":
        text = "You said: `%s`" % event["message"]["text"]
    else:
        return
    return web.Response(text=text)


if __name__ == "__main__":
    _LOGGER.setLevel(logging.DEBUG)
    _LOGGER.debug("Debug mode turned on")

    app.add_routes(routes)
    web.run_app(app)
