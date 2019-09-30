#!/usr/bin/env python3
# sesheta-actions
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

import logging

import requests
from requests.exceptions import HTTPError

from thoth.common import init_logging


_LOGGER = logging.getLogger("merge_master_into_pullrequest")


def merge_master_into_pullrequest(owner: str, repo: str, pull_request: int, token: str = None):
    """Merge the master branch into the Pull Request."""
    if token == None:
        _LOGGER.error("No GitHub Access Token has been provided.")
        raise Exception()

    try:
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_request}",
            headers={"Accept": "application/vnd.github.hawkgirl-preview+json"},
        )

        _r = response.json()

        mergeable = _r["mergeable"]
        rebaseable = _r["rebaseable"]

        # TODO if both are None, we need to come back in a few seconds, github has not finished a background task
        if rebaseable and mergeable:
            _LOGGER.info(f"rebasing Pull Request {pull_request} in {owner}/{repo} into master")
            response = requests.put(
                f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_request}/update-branch",
                headers={"Accept": "application/vnd.github.lydian-preview+json", "Authorization": f"token {token}"},
            )

        response.raise_for_status()
    except HTTPError as http_err:
        _LOGGER.exception(f"HTTP error occurred: {http_err}", http_err)
    except Exception as err:
        _LOGGER.exception(f"Other error occurred: {err}", err)


if __name__ == "__main__":
    pass
