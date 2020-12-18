#!/usr/bin/env python3
# sefkhet-abwy
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


"""Sesheta."""

__title__ = "sefkhet-abwy"
__version__ = "0.20.2"


async def get_github_client(github_app, account):
    """Get GitHub Client by Account."""
    github_app_installations = await github_app.get_installations()
    target_github_app_installation = next(
        (i for n, i in github_app_installations.items() if i._metadata.account["login"] == account), None,
    )

    return target_github_app_installation.get_github_api_client()
