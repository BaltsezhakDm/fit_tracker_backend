import os
import aiofiles
from typing import List
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi_pagination import Page, paginate
from src.api.schemas.schemas import ExerciseCreate, ExerciseRead, ExerciseUpdate
from src.application.services.exercise import ExerciseService
from src.api.dependencies import get_exercise_service, get_current_user
from src.domain.entities import User

router = APIRouter(prefix="/exercises", tags=["Exercises"])

@router.post("/", response_model=ExerciseRead)
async def create_exercise(exercise: ExerciseCreate, service: ExerciseService = Depends(get_exercise_service)):
    return await service.create_exercise(**exercise.model_dump())

@router.get("/", response_model=Page[ExerciseRead])
async def list_exercises(
    service: ExerciseService = Depends(get_exercise_service),
):
    exercises = await service.get_all_exercises()
    return paginate(exercises)

@router.get("/{exercise_id}", response_model=ExerciseRead)
async def get_exercise(exercise_id: int, service: ExerciseService = Depends(get_exercise_service)):
    exercise = await service.get_exercise(exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise

@router.patch("/{exercise_id}", response_model=ExerciseRead)
async def update_exercise(exercise_id: int, exercise_data: ExerciseUpdate, service: ExerciseService = Depends(get_exercise_service)):
    exercise = await service.get_exercise(exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    for key, value in exercise_data.model_dump(exclude_unset=True).items():
        setattr(exercise, key, value)

    return await service.update_exercise(exercise)

@router.delete("/{exercise_id}")
async def delete_exercise(exercise_id: int, service: ExerciseService = Depends(get_exercise_service)):
    await service.delete_exercise(exercise_id)
    return {"status": "success"}

@router.post("/{exercise_id}/blacklist")
async def blacklist_exercise(
    exercise_id: int,
    service: ExerciseService = Depends(get_exercise_service),
    current_user: User = Depends(get_current_user)
):
    await service.blacklist_exercise(current_user.id, exercise_id)
    return {"status": "success"}

@router.post("/{exercise_id}/media")
async def upload_media(exercise_id: int, file: UploadFile = File(...), service: ExerciseService = Depends(get_exercise_service)):
    """
    Upload media file for an exercise.
    """
    exercise = await service.get_exercise(exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    file_path = f"static/uploads/{exercise_id}_{file.filename}"
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    exercise.media_url = f"/static/uploads/{exercise_id}_{file.filename}"
    await service.update_exercise(exercise)

    return {"media_url": exercise.media_url}
