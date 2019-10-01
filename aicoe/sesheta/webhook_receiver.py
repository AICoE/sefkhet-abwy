#!/usr/bin/env python3
# Sesheta
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


"""This will handle all the GitHub webhooks."""


import asyncio
import pathlib

from octomachinery.app.server.runner import run as run_app
from octomachinery.app.routing import process_event_actions
from octomachinery.app.routing.decorators import process_webhook_payload
from octomachinery.app.runtime.context import RUNTIME_CONTEXT
from octomachinery.github.api.app_client import GitHubApp
from octomachinery.github.config.app import GitHubAppIntegrationConfig


GITHUB_ORG = "thoth-station"
GITHUB_APP_ID = 30790
GITHUB_APP_PRIVATE_KEY_PATH = pathlib.Path("review-manager.2019-09-30.private-key.pem").expanduser().resolve()


@process_event_actions("issues", {"opened"})
@process_webhook_payload
async def on_issue_opened(*, action, issue, repository, sender, installation, assignee=None, changes=None):
    """Whenever an issue is opened, greet the author and say thanks."""
    github_api = RUNTIME_CONTEXT.app_installation_client

    print(issue)


async def get_github_client(github_app, account):
    github_app_installations = await github_app.get_installations()
    target_github_app_installation = next(
        (i for n, i in github_app_installations.items() if i._metadata.account["login"] == account), None
    )
    return target_github_app_installation.get_github_api_client()


async def main():
    github_app_config = GitHubAppIntegrationConfig(
        app_id=GITHUB_APP_ID,
        private_key=GITHUB_APP_PRIVATE_KEY_PATH.read_text(),
        app_name="Sesehta",
        app_version="0.1.0",
        app_url="https://github.com/apps/review-manager",
    )
    github_app = GitHubApp(github_app_config)

    github_api = await get_github_client(github_app, GITHUB_ORG)
    user = await github_api.getitem(f"/users/{GITHUB_ORG}")

    print(f'User found: {user["login"]}')
    print(f"Rate limit stats: {github_api.rate_limit!s}")


if __name__ == "__main__":
    asyncio.run(main())
