from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from src.api.schemas.schemas import WorkoutSessionRead, WorkoutExerciseRead, WorkoutSetCreate, WorkoutSetRead
from src.application.services.workout import WorkoutService
from src.api.dependencies import get_workout_service

router = APIRouter(prefix="/workouts", tags=["Workouts"])

@router.post("/start", response_model=WorkoutSessionRead)
async def start_workout(user_id: int, plan_id: Optional[int] = None, service: WorkoutService = Depends(get_workout_service)):
    return await service.start_workout(user_id, plan_id)

@router.post("/{session_id}/exercises", response_model=WorkoutExerciseRead)
async def add_exercise(session_id: int, exercise_id: int, service: WorkoutService = Depends(get_workout_service)):
    return await service.add_exercise_to_workout(session_id, exercise_id)

@router.post("/exercises/{workout_exercise_id}/sets", response_model=WorkoutSetRead)
async def add_set(workout_exercise_id: int, workout_set: WorkoutSetCreate, service: WorkoutService = Depends(get_workout_service)):
    return await service.add_set(workout_exercise_id, **workout_set.model_dump())

@router.patch("/exercises/{workout_exercise_id}/swap", response_model=WorkoutExerciseRead)
async def hot_swap(workout_exercise_id: int, new_exercise_id: int, service: WorkoutService = Depends(get_workout_service)):
    try:
        return await service.hot_swap_exercise(workout_exercise_id, new_exercise_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{session_id}/complete", response_model=WorkoutSessionRead)
async def complete_workout(session_id: int, service: WorkoutService = Depends(get_workout_service)):
    try:
        return await service.complete_workout(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/user/{user_id}/history", response_model=List[WorkoutSessionRead])
async def get_history(user_id: int, service: WorkoutService = Depends(get_workout_service)):
    return await service.get_workout_history(user_id)
