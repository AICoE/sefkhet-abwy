#!/usr/bin/env python3
# Sefkhet-Abwy
# Copyright(C) 2019-2022 The Authors of Project Thoth
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

SPACE = os.getenv("SESHETA_THOTH_DEVOPS_SPACE", None)


def main():
    """Get a List of user from a Google Chat Space and print it to stdout."""
    if SPACE is not None:
        scopes = ["https://www.googleapis.com/auth/chat.bot"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name("sesheta-chatbot-b5a97b40eeab.json", scopes)
        http_auth = credentials.authorize(Http())

        chat = build("chat", "v1", http=http_auth)

        response = chat.spaces().members().list(parent=SPACE)

        if response is not None:
            r = response.execute()

        for member in r["memberships"]:
            print(f"\"{member['member']['displayName']}\": \"{member['member']['name'].replace('users/', '')}\",")


if __name__ == "__main__":
    main()
