import pytest


@pytest.mark.anyio
async def test_root(ac):
    response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }