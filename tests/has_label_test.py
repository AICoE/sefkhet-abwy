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

from aicoe.sesheta.actions.pull_request import has_label


@pytest.fixture
def no_needs_rebase_labeled_pull_request():
    with open("fixtures/pull_request_148.json") as json_file:
        return json.load(json_file)


@pytest.fixture
def has_needs_rebase_labeled():
    with open("fixtures/pull_request_2.json") as json_file:
        return json.load(json_file)


class TestHasLabel:
    @pytest.mark.asyncio
    async def test_label_is_not_present(self, no_needs_rebase_labeled_pull_request):
        assert no_needs_rebase_labeled_pull_request is not None

        assert not has_label(no_needs_rebase_labeled_pull_request, "do-not-merge/needs-rebase")

    @pytest.mark.asyncio
    async def test_label_is_present(self, has_needs_rebase_labeled):
        assert has_needs_rebase_labeled is not None

        assert has_label(has_needs_rebase_labeled, "do-not-merge/needs-rebase")
