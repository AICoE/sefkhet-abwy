#!/usr/bin/env python3
# Sefkhet-Abwy
# Copyright(C) 2019, 2020 Christoph Görn, Sai Sankar Gochhayat
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

"""Add all the messages to be used by chatbot here."""

# TODO add more message types like deliver or tag release of.
HELP_MESSAGE = """
    Here are some thing's you can do -
    - Create releases using Kebechet -
      - `create new <minor/major/patch> release for <repository name>` to create a minor release.
    - Get a listing of Thoth inhabitants
      - `get thoth inhabitants` to get a listing of Thoth inhabitants in random order
      - `gti` is the abbreviated form
    - Get one Thoth inhabitant, randomly
      - `get random thoth inhabitant` to randomly pick one Thoth inhabitant
      - `grti` is the abbreviated form
    - Trigger Kebechet updates for all the Thoth repositories that depend on thoth-storages
      - `schema updated` to open "Kebechet update" on all the repositories that use thoth-storages
    """
