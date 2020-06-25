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


import pytest

from aicoe.sesheta.actions.common import conclude_reviewer_list


class TestConcludeReviewers:  # noqa: D101
    @pytest.mark.asyncio
    async def test_conclude_reviewers_no_org(self):  # noqa: D102
        reviewers = await conclude_reviewer_list(repo="repo")

        assert reviewers is None

    @pytest.mark.asyncio
    async def test_conclude_reviewers_no_repo(self):  # noqa: D102
        reviewers = await conclude_reviewer_list("org")

        assert reviewers is None

    @pytest.mark.asyncio
    async def test_conclude_reviewers_no_codeowners_file(self):  # noqa: D102
        reviewers = await conclude_reviewer_list("thoth-station", "user-api")

        assert reviewers is not None
        assert len(reviewers) >= 1
        assert reviewers[0] == "fridex"

    @pytest.mark.asyncio
    async def test_conclude_reviewers(self):  # noqa: D102
        reviewers = await conclude_reviewer_list("thoth-station", "storages")

        assert reviewers is not None
