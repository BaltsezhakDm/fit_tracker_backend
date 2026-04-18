import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.infrastructure.db.models import Base
from src.infrastructure.db.session import engine
import asyncio

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
async def test_full_workout_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 0. Auth
        resp = await ac.post("/auth/telegram", json={"initData": "user=%7B%22id%22%3A12345%2C%22username%22%3A%22testuser%22%7D&hash=mock"})
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Get current user
        resp = await ac.get("/users/me", headers=headers)
        assert resp.status_code == 200
        user_id = resp.json()["id"]

        # 2. Create Exercise
        resp = await ac.post("/exercises/", headers=headers, json={
            "name": "Squat",
            "primary_muscle_group": "Legs",
            "secondary_muscle_groups": ["Glutes"],
            "description": "Standard barbell squat"
        })
        assert resp.status_code == 200
        exercise_id = resp.json()["id"]

        # 3. Create Program and Plan
        resp = await ac.post("/programs/", headers=headers, json={"name": "Powerlifting"})
        program_id = resp.json()["id"]

        resp = await ac.post("/programs/plans", headers=headers, json={"program_id": program_id, "name": "Leg Day"})
        plan_id = resp.json()["id"]

        # 4. Start Workout from Plan
        resp = await ac.post(f"/workouts/start?plan_id={plan_id}", headers=headers)
        assert resp.status_code == 200
        session_id = resp.json()["id"]

        # 5. Add Exercise and Set
        resp = await ac.post(f"/workouts/{session_id}/exercises?exercise_id={exercise_id}", headers=headers)
        print(f"DEBUG: add exercise resp: {resp.json()}")
        workout_exercise_id = resp.json()["id"]

        resp = await ac.post(f"/workouts/exercises/{workout_exercise_id}/sets", headers=headers, json={
            "reps": 10,
            "weight": 100.0
        })
        assert resp.status_code == 200

        # 6. Update Exercise (CRUD check)
        resp = await ac.patch(f"/exercises/{exercise_id}", headers=headers, json={"comment": "New comment"})
        assert resp.status_code == 200
        assert resp.json()["comment"] == "New comment"

        # 7. Complete Workout
        resp = await ac.post(f"/workouts/{session_id}/complete", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

        # 8. Analytics
        resp = await ac.get(f"/analytics/user/{user_id}/exercise/{exercise_id}/progression", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 1
