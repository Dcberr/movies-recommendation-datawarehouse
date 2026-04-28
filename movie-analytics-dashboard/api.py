import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.ai.pipeline.recommender import recommend_with_context


app = FastAPI(title="Movie AI Service", version="1.0.0")


class RecommendationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Movie preference in natural language")
    top_k: int = Field(default=10, ge=1, le=20)


@app.get("/health")
def healthcheck():
    return {"status": "ok"}


@app.post("/recommend")
def recommend_movies(payload: RecommendationRequest):
    prompt = payload.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt must not be empty.")

    return recommend_with_context(prompt, top_k=payload.top_k)
