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

"""Sesheta's actions Tests."""


import json
import pytest

from aicoe.sesheta.actions.pull_request import has_label, is_rebaseable


@pytest.fixture
def pr_needs_rebase():
    with open("fixtures/pull_request_150.json") as json_file:
        return json.load(json_file)


@pytest.fixture
def has_needs_rebase_label():
    with open("fixtures/pull_request_148.json") as json_file:
        return json.load(json_file)


@pytest.fixture
def doesnt_need_rebase():
    with open("fixtures/pull_request_2.json") as json_file:
        return json.load(json_file)


class TestNeedsRebase:
    @pytest.mark.asyncio
    async def test_pull_request_needs_rebase(self, pr_needs_rebase, has_needs_rebase_label):
        assert pr_needs_rebase is not None
        assert has_needs_rebase_label is not None

        has_needs_rebase_label_actual = await is_rebaseable(has_needs_rebase_label)
        pr_needs_rebase_actual = await is_rebaseable(pr_needs_rebase)

        assert has_needs_rebase_label_actual == False
        assert pr_needs_rebase_actual == False

    @pytest.mark.asyncio
    async def test_pull_request_doesnt_need_rebase(self, doesnt_need_rebase):
        assert doesnt_need_rebase is not None

        doesnt_need_rebase_actual = await is_rebaseable(doesnt_need_rebase)

        assert not doesnt_need_rebase_actual
