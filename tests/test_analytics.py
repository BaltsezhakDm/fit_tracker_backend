import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.infrastructure.db.models import Base
from src.infrastructure.db.session import engine
import asyncio
from datetime import datetime, UTC, timedelta

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
async def test_analytics_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Auth
        resp = await ac.post("/auth/telegram", json={"initData": "user=%7B%22id%22%3A12345%2C%22username%22%3A%22testuser%22%7D&hash=mock"})
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create Exercise
        resp = await ac.post("/exercises/", headers=headers, json={
            "name": "Bench Press",
            "primary_muscle_group": "Chest"
        })
        exercise_id = resp.json()["id"]

        # 3. Perform a workout
        resp = await ac.post("/workouts/start", headers=headers)
        session_id = resp.json()["id"]

        resp = await ac.post(f"/workouts/{session_id}/exercises?exercise_id={exercise_id}", headers=headers)
        workout_exercise_id = resp.json()["id"]

        await ac.post(f"/workouts/exercises/{workout_exercise_id}/sets", headers=headers, json={
            "reps": 10,
            "weight": 100.0
        })

        await ac.post(f"/workouts/{session_id}/complete", headers=headers)

        # 4. Test Summary
        resp = await ac.get("/analytics/summary", headers=headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["total_volume"] == 1000.0
        assert data["workouts_count"] == 1
        assert data["records_count"] == 1

        # 5. Test Workload
        resp = await ac.get("/analytics/workload?period=week", headers=headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert len(data) == 7
        assert any(d["volume"] == 1000.0 for d in data)

        # 6. Test Records
        resp = await ac.get("/analytics/records", headers=headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert len(data) == 1
        assert data[0]["exercise_name"] == "Bench Press"
        assert data[0]["weight"] == 100.0
