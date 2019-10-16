import pytest

from aicoe.sesheta.actions.common import conclude_reviewer_list


class TestConcludeReviewers:
    @pytest.mark.asyncio
    async def test_conclude_reviewers_no_org(self):
        reviewers = await conclude_reviewer_list(repo="repo")

        assert reviewers is None

    @pytest.mark.asyncio
    async def test_conclude_reviewers_no_repo(self):
        reviewers = await conclude_reviewer_list("org")

        assert reviewers is None

    @pytest.mark.asyncio
    async def test_conclude_reviewers_no_codeowners_file(self):
        reviewers = await conclude_reviewer_list("thoth-station", "user-api")

        assert reviewers is not None
        assert len(reviewers) >= 1
        assert reviewers[0] == "fridex"

    @pytest.mark.asyncio
    async def test_conclude_reviewers(self):
        reviewers = await conclude_reviewer_list("thoth-station", "storages")

        assert reviewers is not None
