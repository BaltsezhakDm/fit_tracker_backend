import pytest
import time
import hmac
import hashlib
import urllib.parse
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.core.config import settings
from src.infrastructure.db.models import Base
from src.infrastructure.db.session import engine
import asyncio

def generate_tg_data(bot_token: str, user_id: int = 12345, username: str = "testuser"):
    auth_date = int(time.time())
    raw_params = {
        "auth_date": str(auth_date),
        "query_id": "AAH-....",
        "user": f'{{"id":{user_id},"username":"{username}"}}'
    }
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(raw_params.items())])
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    valid_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return urllib.parse.urlencode({**raw_params, "hash": valid_hash})

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_get_exercise():
    settings.TELEGRAM_BOT_TOKEN = "123456:ABC-DEF"
    init_data = generate_tg_data(settings.TELEGRAM_BOT_TOKEN)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/auth/telegram", json={"initData": init_data})
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = await ac.post("/exercises/", headers=headers, json={
            "name": "Deadlift",
            "primary_muscle_group": "Back",
            "secondary_muscle_groups": ["Legs"],
            "description": "A compound exercise that works the entire body.",
            "media_url": "https://example.com/deadlift.jpg"
        })
        assert resp.status_code == 200
        exercise_id = resp.json()["id"]

        resp = await ac.get(f"/exercises/{exercise_id}", headers=headers)
        assert resp.status_code == 200
        data = resp.json()

        assert data["id"] == exercise_id
        assert data["name"] == "Deadlift"
        assert data["description"] == "A compound exercise that works the entire body."
        assert data["media_url"] == "https://example.com/deadlift.jpg"
