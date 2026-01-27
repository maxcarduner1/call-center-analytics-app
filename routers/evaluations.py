"""
Router for human evaluation endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import json

from services.human_evaluations_service import (
    get_human_evaluation,
    save_human_evaluation,
    delete_human_evaluation,
    get_all_evaluated_call_ids,
    ensure_human_evaluations_table
)

router = APIRouter(prefix="/api/evaluations", tags=["evaluations"])


class HumanEvaluationRequest(BaseModel):
    """Request model for creating/updating a human evaluation."""
    evaluator_name: str
    scorecard_overrides: dict
    total_score_override: int
    feedback_text: Optional[str] = ""


@router.post("/init-table")
async def initialize_table():
    """
    Initialize the human_evaluations table if it doesn't exist.
    This endpoint should be called once during setup.
    """
    try:
        ensure_human_evaluations_table()
        return {"status": "success", "message": "Human evaluations table initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{call_id}")
async def get_evaluation(call_id: str):
    """
    Get human evaluation for a specific call.
    Returns 404 if no evaluation exists.
    """
    try:
        row = get_human_evaluation(call_id)
        
        if row is None:
            raise HTTPException(status_code=404, detail="No human evaluation found for this call")
        
        # Parse the scorecard JSON if it's a string
        scorecard_overrides = row[4] if len(row) > 4 else {}
        if isinstance(scorecard_overrides, str):
            scorecard_overrides = json.loads(scorecard_overrides)
        
        return {
            "evaluation_id": row[0],
            "call_id": row[1],
            "evaluator_name": row[2],
            "evaluation_date": str(row[3]) if row[3] else None,
            "scorecard_overrides": scorecard_overrides,
            "total_score_override": row[5] if len(row) > 5 else None,
            "feedback_text": row[6] if len(row) > 6 else ""
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{call_id}")
async def save_evaluation(call_id: str, evaluation: HumanEvaluationRequest):
    """
    Save or update a human evaluation for a call.
    """
    try:
        row = save_human_evaluation(
            call_id=call_id,
            evaluator_name=evaluation.evaluator_name,
            scorecard_overrides=evaluation.scorecard_overrides,
            total_score_override=evaluation.total_score_override,
            feedback_text=evaluation.feedback_text or ""
        )
        
        if row is None:
            raise HTTPException(status_code=500, detail="Failed to save evaluation")
        
        # Parse the scorecard JSON if it's a string
        scorecard_overrides = row[4] if len(row) > 4 else {}
        if isinstance(scorecard_overrides, str):
            scorecard_overrides = json.loads(scorecard_overrides)
        
        return {
            "evaluation_id": row[0],
            "call_id": row[1],
            "evaluator_name": row[2],
            "evaluation_date": str(row[3]) if row[3] else None,
            "scorecard_overrides": scorecard_overrides,
            "total_score_override": row[5] if len(row) > 5 else None,
            "feedback_text": row[6] if len(row) > 6 else ""
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{call_id}")
async def delete_evaluation(call_id: str):
    """
    Delete a human evaluation for a call.
    """
    try:
        deleted = delete_human_evaluation(call_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="No evaluation found to delete")
        
        return {"status": "success", "message": "Evaluation deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_evaluated_calls():
    """
    Get list of all call IDs that have human evaluations.
    """
    try:
        call_ids = get_all_evaluated_call_ids()
        
        return {
            "count": len(call_ids),
            "evaluated_call_ids": call_ids
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
