from typing import List
from fastapi import APIRouter, Depends
from src.api.schemas.schemas import (
    TrainingProgramCreate, TrainingProgramRead, TrainingProgramUpdate,
    TrainingPlanCreate, TrainingPlanRead, TrainingPlanUpdate,
    PlanExerciseBase, PlanExerciseRead
)
from src.application.services.program import ProgramService
from src.api.dependencies import get_program_service

router = APIRouter(prefix="/programs", tags=["Programs & Plans"])

@router.post("/", response_model=TrainingProgramRead)
async def create_program(program: TrainingProgramCreate, service: ProgramService = Depends(get_program_service)):
    return await service.create_program(**program.model_dump())

@router.get("/user/{user_id}", response_model=List[TrainingProgramRead])
async def list_user_programs(user_id: int, service: ProgramService = Depends(get_program_service)):
    return await service.get_user_programs(user_id)

@router.post("/plans", response_model=TrainingPlanRead)
async def add_plan(plan: TrainingPlanCreate, service: ProgramService = Depends(get_program_service)):
    return await service.add_plan_to_program(**plan.model_dump())

@router.post("/plans/{plan_id}/exercises")
async def add_exercise_to_plan(plan_id: int, exercise: PlanExerciseBase, service: ProgramService = Depends(get_program_service)):
    await service.add_exercise_to_plan(plan_id, **exercise.model_dump())
    return {"status": "success"}

@router.get("/plans/{plan_id}/exercises", response_model=List[PlanExerciseRead])
async def list_plan_exercises(plan_id: int, service: ProgramService = Depends(get_program_service)):
    return await service.get_plan_exercises(plan_id)

@router.patch("/{program_id}", response_model=TrainingProgramRead)
async def update_program(program_id: int, program_data: TrainingProgramUpdate, service: ProgramService = Depends(get_program_service)):
    updated = await service.update_program(program_id, **program_data.model_dump(exclude_unset=True))
    if not updated:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Program not found")
    return updated

@router.delete("/{program_id}")
async def delete_program(program_id: int, service: ProgramService = Depends(get_program_service)):
    await service.delete_program(program_id)
    return {"status": "success"}

@router.patch("/plans/{plan_id}", response_model=TrainingPlanRead)
async def update_plan(plan_id: int, plan_data: TrainingPlanUpdate, service: ProgramService = Depends(get_program_service)):
    updated = await service.update_plan(plan_id, **plan_data.model_dump(exclude_unset=True))
    if not updated:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Plan not found")
    return updated

@router.delete("/plans/{plan_id}")
async def delete_plan(plan_id: int, service: ProgramService = Depends(get_program_service)):
    await service.delete_plan(plan_id)
    return {"status": "success"}
