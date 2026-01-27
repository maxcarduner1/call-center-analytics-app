"""
Router for call center analytics endpoints.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import json

from services.calls_service import list_calls, get_call_by_id, get_all_ccr_ids, get_ccr_aggregate_stats, merge_ai_and_human_scores
from services.human_evaluations_service import get_human_evaluation

router = APIRouter(prefix="/api", tags=["calls"])


@router.get("/calls")
async def get_calls(
    member_id: Optional[str] = Query(None, description="Filter by member ID"),
    min_score: Optional[int] = Query(None, description="Minimum total score"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    call_center_rep_id: Optional[str] = Query(None, description="Filter by call center rep ID")
):
    """
    List all calls with optional filtering.
    Includes indicator if call has human evaluation override.
    """
    try:
        rows = list_calls(
            member_id=member_id,
            min_score=min_score,
            start_date=start_date,
            end_date=end_date,
            call_center_rep_id=call_center_rep_id
        )
        
        # Convert rows to list of dicts
        calls = []
        for row in rows:
            call_id = row[0]
            
            # Check if this call has a human evaluation
            human_eval = get_human_evaluation(call_id)
            has_override = human_eval is not None
            
            # Use human override score if it exists
            total_score = row[3]
            if has_override and len(human_eval) > 5 and human_eval[5] is not None:
                total_score = human_eval[5]
            
            calls.append({
                "call_id": call_id,
                "member_id": row[1],
                "call_date": str(row[2]) if row[2] else None,
                "total_score": total_score,
                "call_center_rep_id": row[4] if len(row) > 4 else None,
                "has_human_override": has_override
            })
        
        return {
            "count": len(calls),
            "calls": calls
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calls/{call_id}")
async def get_call(call_id: str):
    """
    Get full details of a specific call including transcript and scorecard.
    Merges AI scores with human overrides if they exist.
    """
    try:
        row = get_call_by_id(call_id)
        
        if row is None:
            raise HTTPException(status_code=404, detail="Call not found")
        
        # Parse the scorecard JSON
        scorecard_json = row[4] if len(row) > 4 else {}
        if isinstance(scorecard_json, str):
            scorecard_json = json.loads(scorecard_json)
        
        call_data = {
            "call_id": row[0],
            "member_id": row[1],
            "call_date": row[2],
            "transcript": row[3],
            "scorecard": scorecard_json,
            "total_score": row[5] if len(row) > 5 else None,
            "call_center_rep_id": row[6] if len(row) > 6 else None
        }
        
        # Merge with human evaluation if it exists
        call_data = merge_ai_and_human_scores(call_data)
        
        return call_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ccrs")
async def get_ccrs():
    """
    Get list of all call center representative IDs.
    """
    try:
        rows = get_all_ccr_ids()
        
        # Convert rows to list of CCR IDs
        ccr_ids = [row[0] for row in rows if row[0] is not None]
        
        return {
            "count": len(ccr_ids),
            "ccr_ids": ccr_ids
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ccrs/{ccr_id}/stats")
async def get_ccr_stats(ccr_id: str):
    """
    Get aggregate performance statistics for a specific call center representative.
    """
    try:
        row = get_ccr_aggregate_stats(ccr_id)
        
        if row is None:
            raise HTTPException(status_code=404, detail="CCR not found or has no calls")
        
        return {
            "call_center_rep_id": row[0],
            "total_calls": row[1],
            "avg_score": float(row[2]) if row[2] is not None else None,
            "min_score": row[3],
            "max_score": row[4]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
