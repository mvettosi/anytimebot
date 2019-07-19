from anytimebot import tournament
from asynctest import CoroutineMock, MagicMock, patch
import pytest
import asynctest
import challonge

user = MagicMock(challonge.User(1, 2))


@pytest.mark.asyncio
@asynctest.patch.object(challonge, 'get_user', return_value=user)
async def test_create_tournament(mock_get_user):
    await tournament.create_tournament(1, 2)

    mock_get_user.assert_called()
    user.create_tournament.assert_called()
