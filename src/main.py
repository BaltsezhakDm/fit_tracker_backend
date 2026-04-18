import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from src.api.routers import users, exercises, programs, workouts, analytics, auth
from src.core.config import settings

app = FastAPI(
    title="Fit-Tracker API",
    description="Backend API for fitness tracking following Clean Architecture principles",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(exercises.router)
app.include_router(programs.router)
app.include_router(workouts.router)
app.include_router(analytics.router)

add_pagination(app)

os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Welcome to Fit-Tracker API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
