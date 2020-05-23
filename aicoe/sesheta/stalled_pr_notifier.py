#!/usr/bin/env python3
# Sesheta
# Copyright(C) 2020 Christoph Görn
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


"""This will notify our DevOps Hangout room on stalled PR."""


import os
import asyncio
import logging

from datetime import datetime

import aiohttp

from natural import date

from octomachinery.github.api.tokens import GitHubOAuthToken
from octomachinery.github.api.raw_client import RawGitHubAPI

from thoth.common import init_logging
from aicoe.sesheta.actions import __version__


HEADERS = {
    "Authorization": "bearer 84b784bfdeb13d1e3b00fcc65b657be5d0863cde",
    "X-Sefkeht-Abwy-Version": f"v{__version__}",
}

QUERY = """{
  search(query: "org:thoth-station is:pr is:open sort:desc", type: ISSUE, last: 5) {
    edges {
      node {
        ... on PullRequest {
          url
          title
          createdAt
        }
      }
    }
  }
}
"""


init_logging(logging_env_var_start="SEFKHET__ABWY_LOG_")

_LOGGER = logging.getLogger("thoth.stalled_pr_notifier")
_LOGGER.info(f"Sesheta action: stalled_pr_notifier, Version v{__version__}")
_LOGGER.debug(f"DEBUG mode is enabled")


async def get_stalled_pull_requests():
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.post("https://api.github.com/graphql", json={"query": QUERY}) as resp:
            edges = await resp.json()

    return edges["data"]["search"]["edges"]


if __name__ == "__main__":
    _LOGGER.info(f"looking for stalled Pull Requests...")

    print("Some Pull Requests are stalled:")
    for pr in asyncio.run(get_stalled_pull_requests()):
        created_at = datetime.strptime(pr["node"]["createdAt"], "%Y-%m-%dT%H:%M:%SZ")

        print(f"\t'{pr['node']['title']}' created {date.day(created_at)}")

    _LOGGER.info(f"done wiht my stuff!")
