from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, paginate
from src.api.schemas.schemas import WorkoutSessionRead, WorkoutExerciseRead, WorkoutSetCreate, WorkoutSetRead
from src.application.services.workout import WorkoutService
from src.api.dependencies import get_workout_service, get_current_user
from src.domain.entities import User

router = APIRouter(prefix="/workouts", tags=["Workouts"])

@router.post("/start", response_model=WorkoutSessionRead)
async def start_workout(
    plan_id: Optional[int] = None,
    service: WorkoutService = Depends(get_workout_service),
    current_user: User = Depends(get_current_user)
):
    return await service.start_workout(current_user.id, plan_id)

@router.post("/{session_id}/exercises", response_model=WorkoutExerciseRead)
async def add_exercise(session_id: UUID, exercise_id: int, service: WorkoutService = Depends(get_workout_service)):
    return await service.add_exercise_to_workout(session_id, exercise_id)

@router.post("/exercises/{workout_exercise_id}/sets", response_model=WorkoutSetRead)
async def add_set(workout_exercise_id: UUID, workout_set: WorkoutSetCreate, service: WorkoutService = Depends(get_workout_service)):
    return await service.add_set(workout_exercise_id, **workout_set.model_dump())

@router.patch("/exercises/{workout_exercise_id}/swap", response_model=WorkoutExerciseRead)
async def hot_swap(workout_exercise_id: UUID, new_exercise_id: int, service: WorkoutService = Depends(get_workout_service)):
    try:
        return await service.hot_swap_exercise(workout_exercise_id, new_exercise_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{session_id}/complete", response_model=WorkoutSessionRead)
async def complete_workout(session_id: UUID, service: WorkoutService = Depends(get_workout_service)):
    try:
        return await service.complete_workout(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/history", response_model=Page[WorkoutSessionRead])
async def get_history(
    service: WorkoutService = Depends(get_workout_service),
    current_user: User = Depends(get_current_user)
):
    history = await service.get_workout_history(current_user.id)
    return paginate(history)

@router.delete("/{session_id}")
async def delete_workout_session(session_id: UUID, service: WorkoutService = Depends(get_workout_service)):
    await service.delete_workout_session(session_id)
    return {"status": "success"}

@router.get("/{session_id}/exercises", response_model=List[WorkoutExerciseRead])
async def get_session_exercises(session_id: UUID, service: WorkoutService = Depends(get_workout_service)):
    return await service.get_session_exercises(session_id)

@router.get("/exercises/{workout_exercise_id}/sets", response_model=List[WorkoutSetRead])
async def get_workout_exercise_sets(workout_exercise_id: UUID, service: WorkoutService = Depends(get_workout_service)):
    return await service.get_workout_exercise_sets(workout_exercise_id)
