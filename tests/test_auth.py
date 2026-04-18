import pytest
import hashlib
import hmac
import urllib.parse
import time
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.core.config import settings
from src.infrastructure.db.models import Base
from src.infrastructure.db.session import engine

@pytest.fixture(autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

def generate_tg_data(bot_token: str, user_id: int = 12345, username: str = "testuser", expired: bool = False):
    auth_date = int(time.time())
    if expired:
        auth_date -= 100000  # More than 24 hours

    raw_params = {
        "auth_date": str(auth_date),
        "query_id": "AAH-....",
        "user": f'{{"id":{user_id},"username":"{username}"}}'
    }
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(raw_params.items())])
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    valid_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    return urllib.parse.urlencode({**raw_params, "hash": valid_hash})

@pytest.mark.asyncio
async def test_auth_telegram_success():
    # Use a specific token for testing
    settings.TELEGRAM_BOT_TOKEN = "123456:ABC-DEF"
    init_data = generate_tg_data(settings.TELEGRAM_BOT_TOKEN)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/auth/telegram", json={"initData": init_data})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_auth_telegram_invalid_signature():
    settings.TELEGRAM_BOT_TOKEN = "123456:ABC-DEF"
    init_data = generate_tg_data("wrong_token")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/auth/telegram", json={"initData": init_data})
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid Telegram signature"

@pytest.mark.asyncio
async def test_auth_telegram_expired():
    settings.TELEGRAM_BOT_TOKEN = "123456:ABC-DEF"
    init_data = generate_tg_data(settings.TELEGRAM_BOT_TOKEN, expired=True)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/auth/telegram", json={"initData": init_data})
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Auth data expired"

@pytest.mark.asyncio
async def test_auth_telegram_missing_hash():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/auth/telegram", json={"initData": "user={}"})
        assert resp.status_code == 400
        assert "Missing hash" in resp.json()["detail"]
