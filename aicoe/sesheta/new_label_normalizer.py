#!/usr/bin/env python3
# Sefkeht-Abwy
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


"""This will normalize some standard labels."""


import os
import asyncio
import logging
import time
import json

from datetime import datetime
from string import Template

from aiographql.client import GraphQLClient, GraphQLResponse, GraphQLRequest

import aiohttp

from thoth.common import init_logging

from aicoe.sesheta.actions.label import GITHUB_DEFAULT_LABELS, DEFAULT_LABELS, create_or_update_label


__version__ = "0.1.0"


init_logging(logging_env_var_start="SEFKHET__ABWY_LOG_")

_LOGGER = logging.getLogger("thoth.labelnormalizer")
_LOGGER.setLevel(logging.DEBUG if bool(int(os.getenv("DEBUG", 0))) else logging.INFO)

_LOGGER.info(f"Sesheta action: new_label_normalizer, Version v{__version__}")
_LOGGER.debug(f"DEBUG mode is enabled")


ALL_REPOSITORIES_INCLUDING_LABELS_CURSOR = Template(
    """
{
  organization(login: "$login") {
    repositories(first: 50, after: "$cursor") {
      totalCount
      edges {
        node {
          id
          name
          isArchived
          labels(first: 100) {
            totalCount
            nodes {
              name
            }
            pageInfo {
              endCursor
              hasNextPage
            }
          }
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
""",
)

ALL_REPOSITORIES_INCLUDING_LABELS = Template(
    """
{
  organization(login: "$login") {
    repositories(first: 50) {
      totalCount
      edges {
        node {
          id
          name
          isArchived
          labels(first: 100) {
            totalCount
            nodes {
              name
            }
            pageInfo {
              endCursor
              hasNextPage
            }
          }
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
""",
)

CREATE_LABEL = Template(
    """
mutation AddLabel {
  createLabel(input:{repositoryId:"$id", name:"$name", color:"$color", description: "$desc"}) {
    label {
      id
    }
  }
}
""",
)


async def _get_repositories(login: str, cursor: str = None) -> GraphQLResponse:
    """Get Repositories and their labels based on a cursor."""
    token = os.getenv("GITHUB_ACCESS_TOKEN")
    client = GraphQLClient(endpoint="https://api.github.com/graphql", headers={"Authorization": f"Bearer {token}"})

    if cursor is not None:
        request = GraphQLRequest(query=ALL_REPOSITORIES_INCLUDING_LABELS_CURSOR.substitute(login=login, cursor=cursor))
    else:
        request = GraphQLRequest(query=ALL_REPOSITORIES_INCLUDING_LABELS.substitute(login=login))

    return await client.query(request=request)


async def get_repositories(login: str = "thoth-station") -> dict:
    """Get all Repositories using pagination, only Repositories that are not archived will be returned."""
    allRepos = []
    hasNextPage = True
    afterCursor = None
    totalReposCollected = 0

    while hasNextPage:
        _repos = await _get_repositories(login, afterCursor)
        repos = _repos.json["data"]["organization"]["repositories"]

        reposInThisResult = len(repos["edges"])
        totalReposCollected = totalReposCollected + reposInThisResult
        totalRepos = repos["totalCount"]

        _LOGGER.debug("total number of repositories: {0}".format(totalRepos))
        _LOGGER.debug("repositories in this result: {0}".format(reposInThisResult))
        _LOGGER.debug("repositories collected: {0}".format(totalReposCollected))
        _LOGGER.debug("pageInfo: %s", repos["pageInfo"])

        for repo in repos["edges"]:
            if not repo["node"]["isArchived"]:
                allRepos.append(repo["node"])

                # TODO we could go ahead and check if we need to get some more labels due to pagination

        hasNextPage = repos["pageInfo"]["hasNextPage"]
        afterCursor = repos["pageInfo"]["endCursor"]

    _LOGGER.debug("total repositories collected: {0}".format(len(allRepos)))

    with open("allRepos.json", "w", encoding="utf-8") as f:
        json.dump(allRepos, f, ensure_ascii=False, indent=4)

    return allRepos


async def reconcile_labels(repo: dict):
    """Reconcile Labels of the given Repository."""
    _LOGGER.info("reconciling labels of {0}".format(repo["name"]))

    _LOGGER.debug(
        "total number of labels: '{0}', hasNextPage: {1}".format(
            repo["labels"]["totalCount"], repo["labels"]["pageInfo"]["hasNextPage"],
        ),
    )

    if repo["labels"]["pageInfo"]["hasNextPage"]:
        _LOGGER.error("for {0} we didnt get all labels!".format(repo["name"]))

    expectedLabels = {l["name"] for l in DEFAULT_LABELS}
    presentLabels = {l["name"] for l in repo["labels"]["nodes"]}
    _LOGGER.debug("expected labels: {0}".format(expectedLabels))
    _LOGGER.debug("labels present: {0}".format(presentLabels))

    missingLabels = expectedLabels - presentLabels
    _LOGGER.debug("missing labels: {0}".format(missingLabels))

    if len(missingLabels) == 0:
        _LOGGER.info("{0} does not need label reconciliation".format(repo["name"]))

    # TODO some exception handling would be nice...
    token = os.getenv("GITHUB_ACCESS_TOKEN")
    client = GraphQLClient(
        endpoint="https://api.github.com/graphql",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.bane-preview+json"},
    )

    for label in DEFAULT_LABELS:
        if label["name"] in missingLabels:
            mutation = CREATE_LABEL.substitute(
                id=repo["id"], name=label["name"], color=label["color"], desc=label["description"],
            )
            _LOGGER.debug("updating {0} in {1}, mutation: {2}".format(label["name"], repo["name"], mutation))

            request = GraphQLRequest(query=mutation, operation="AddLabel")
            # _LOGGER.debug(request)
            response = await client.query(request=request)
            # _LOGGER.debug(response)


async def main():
    """Execute the main function."""
    repos = []

    if os.path.exists("allRepos.json"):
        _LOGGER.debug("cache file exists: reading it...")
        with open("allRepos.json") as f:
            repos = json.load(f)
    else:
        _LOGGER.debug("querying github, there was no cache file...")
        repos = await get_repositories("thoth-station")

    for repo in repos:
        await reconcile_labels(repo)


if __name__ == "__main__":
    asyncio.run(main())
