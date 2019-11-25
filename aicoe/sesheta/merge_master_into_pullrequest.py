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

"""Sesheta actions: merge master into pull request."""


import os

import click
import logging

from thoth.common import init_logging
from aicoe.sesheta.actions import __version__
from aicoe.sesheta.actions.common import cocommand
from aicoe.sesheta.actions.pull_request import merge_master_into_pullrequest


init_logging(logging_env_var_start="SEFKHET__ABWY_LOG_")

_LOGGER = logging.getLogger(__name__)
_LOGGER.info(f"Sesheta action: merge_master_into_pullrequest, Version v{__version__}")


@click.command()
@cocommand
@click.option(
    "--verbose", is_flag=True, default=False, envvar="SESHETA_ACTION_VERBOSE", help="Be verbose about what's going on."
)
@click.option(
    "-r",
    "--dry-run",
    is_flag=True,
    envvar="SESHETA_ACTION_DRY_RUN",
    help="Just a dry run, no changes are made via GitHub API.",
)
@click.option(
    "-t",
    "--github-access-token",
    required=True,
    type=str,
    envvar="SESHETA_ACTION_GITHUB_ACCESS_TOKEN",
    help="A token to authenticate with GitHub.",
)
@click.argument("owner", envvar="SESHETA_ACTION_GITHUB_OWNER")
@click.argument("repo", envvar="SESHETA_ACTION_GITHUB_REPO")
@click.argument("pull_request", envvar="SESHETA_ACTION_GITHUB_PULL_REQUEST")
async def cli(
    owner: str = None,
    repo: str = None,
    pull_request: int = 0,
    verbose: bool = False,
    dry_run: bool = False,
    github_access_token: str = None,
):
    """Command line interface for Sesheta action."""
    # TODO have a global configuration object, so that all subsequent loggers can set their level from it
    if verbose:
        _LOGGER.setLevel(logging.DEBUG)
        _LOGGER.debug("Debug mode turned on")

    # TODO check if owner, repo, pull_request is not None or 0

    triggered = await merge_master_into_pullrequest(
        owner, repo, pull_request, token=github_access_token, dry_run=dry_run
    )

    if not triggered:
        raise Exception("Pull Request update has not been triggered")


if __name__ == "__main__":
    cli()
