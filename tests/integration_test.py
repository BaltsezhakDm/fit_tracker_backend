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
        # 1. Register User
        resp = await ac.post("/users/", json={"telegram_id": 12345, "username": "testuser"})
        assert resp.status_code == 200
        user_id = resp.json()["id"]

        # 2. Create Exercise
        resp = await ac.post("/exercises/", json={
            "name": "Squat",
            "primary_muscle_group": "Legs",
            "secondary_muscle_groups": ["Glutes"],
            "description": "Standard barbell squat"
        })
        assert resp.status_code == 200
        exercise_id = resp.json()["id"]

        # 3. Create Program and Plan
        resp = await ac.post("/programs/", json={"user_id": user_id, "name": "Powerlifting"})
        program_id = resp.json()["id"]

        resp = await ac.post("/programs/plans", json={"program_id": program_id, "name": "Leg Day"})
        plan_id = resp.json()["id"]

        # 4. Start Workout from Plan
        resp = await ac.post(f"/workouts/start?user_id={user_id}&plan_id={plan_id}")
        assert resp.status_code == 200
        session_id = resp.json()["id"]

        # 5. Add Exercise and Set
        resp = await ac.post(f"/workouts/{session_id}/exercises?exercise_id={exercise_id}")
        workout_exercise_id = resp.json()["id"]

        resp = await ac.post(f"/workouts/exercises/{workout_exercise_id}/sets", json={
            "reps": 10,
            "weight": 100.0
        })
        assert resp.status_code == 200

        # 6. Update Exercise (CRUD check)
        resp = await ac.patch(f"/exercises/{exercise_id}", json={"comment": "New comment"})
        assert resp.status_code == 200
        assert resp.json()["comment"] == "New comment"

        # 7. Complete Workout
        resp = await ac.post(f"/workouts/{session_id}/complete")
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

        # 8. Analytics
        resp = await ac.get(f"/analytics/user/{user_id}/exercise/{exercise_id}/progression")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
