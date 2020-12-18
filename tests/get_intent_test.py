#!/usr/bin/env python3
# sesheta-actions
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

"""Sesheta's actions Tests."""


import json
import pytest

from aicoe.sesheta.actions.chat import get_intent


class TestGetIntent:
    """Class to test all the Intent related methods."""

    @pytest.mark.asyncio
    async def test_get_status_intent(self):
        """Test some basic status intents (aka. commands)."""
        i1 = await get_intent("status")
        assert i1 == ("status", 1.0, {})

        i2 = await get_intent("how are you")
        assert i2 == ("status", 1.0, {})

        i3 = await get_intent("How are you?")
        assert i3 == ("status", 1.0, {})
