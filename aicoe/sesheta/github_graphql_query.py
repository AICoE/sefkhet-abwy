#!/usr/bin/env python3
# Sefkhet-Abwy
# Copyright(C) 2019,2020,2022 Christoph Görn
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


"""A base class for GitHub's GraphQL API."""


import os
import asyncio
import logging
import datetime

from aiographql.client import GraphQLClient, GraphQLRequest, GraphQLResponse

from thoth.common import init_logging

from aicoe.sesheta import __version__


init_logging()


_LOGGER = logging.getLogger("aicoe.sesheta.github.graphql")
_LOGGER.setLevel(logging.DEBUG if bool(int(os.getenv("DEBUG", 0))) else logging.INFO)
_LOGGER.info(__version__)


request = GraphQLRequest(
    query="""
query {
  search(query: "is:open is:issue archived:false user:thoth-station label:priority/critical-urgent label:lifecycle/active sort:created-asc created:<2022-01-03", type: ISSUE, first: 100) {
    issueCount
    edges {
      node {
        ... on Issue {
          number
          title
          repository {
            nameWithOwner
          }
          createdAt
          url
        }
      }
    }
  }
}
""",
)


async def main():
    """Call this to run the main method."""
    client = GraphQLClient(
        endpoint="https://api.github.com/graphql",
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"},
    )

    resp: GraphQLResponse = await client.query(request=request)
    _LOGGER.debug(resp.data)
    _LOGGER.info(f"we have fund {resp.data['search']['issueCount']} issues needing attention!")

    for issue in resp.data["search"]["edges"]:
        _LOGGER.info(issue["node"])


if __name__ == "__main__":
    asyncio.run(main())
